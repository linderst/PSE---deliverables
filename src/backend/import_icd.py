import os
import time
import psycopg2
from lxml import etree
from google import genai
from tqdm import tqdm
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "medcode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set!")
genai_client = genai.Client(api_key=GEMINI_API_KEY)

DATA_DIR = os.getenv("DATA_DIR", ".")
XML_FILE = os.path.join(DATA_DIR, "icd10gm2026syst_claml_20250912.xml")
TXT_FILE = os.path.join(DATA_DIR, "icd10gm2026alpha_edvtxt_20250926.txt")

model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
EMBEDDING_DIM = 384


# --------------------------------------------------
# Database Connection
# --------------------------------------------------

conn = psycopg2.connect(
    host=DB_HOST,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)
conn.autocommit = True
cur = conn.cursor()


# --------------------------------------------------
# Create Tables
# --------------------------------------------------

def create_tables():
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    cur.execute("""
    CREATE TABLE IF NOT EXISTS icd_class (
        id SERIAL PRIMARY KEY,
        code VARCHAR(10) UNIQUE NOT NULL,
        kind VARCHAR(50),
        title TEXT,
        definition TEXT,
        parent_code VARCHAR(10),
        is_leaf BOOLEAN,
        para295 CHAR(1),
        para301 CHAR(1),
        sex_code CHAR(1),
        age_low VARCHAR(10),
        age_high VARCHAR(10),
        infectious BOOLEAN,
        content BOOLEAN
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS icd_synonym (
        id SERIAL PRIMARY KEY,
        icd_code VARCHAR(10) REFERENCES icd_class(code),
        term TEXT NOT NULL,
        coding_type INT
    );
    """)

    cur.execute(f"""
    CREATE TABLE IF NOT EXISTS icd_embedding (
        id SERIAL PRIMARY KEY,
        icd_code VARCHAR(10) REFERENCES icd_class(code),
        source_type VARCHAR(20),
        source_id INT,
        embedding vector({EMBEDDING_DIM})
    );
    """)

    # Note: We omit CREATE INDEX here because ivfflat only supports up to 2000
    # dimensions in pgvector. Exact search (sequential scan) is fast enough 
    # for 15,000 ICD codes and 3072 dimensions.
    
    print("Tables created.")


# --------------------------------------------------
# Embedding Function
# --------------------------------------------------

def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []

    embeddings = model.encode(texts)
    return [emb.tolist() for emb in embeddings]


# --------------------------------------------------
# Import XML (Systematic Directory)
# --------------------------------------------------

def import_xml():
    print("Parsing XML...")

    tree = etree.parse(XML_FILE)
    root = tree.getroot()

    namespace = root.nsmap.get(None)

    classes = root.findall(".//{*}Class")

    for cls in tqdm(classes):

        code = cls.attrib.get("code")
        kind = cls.attrib.get("kind")

        title = None
        definition = None
        parent_code = None

        # Title extraction
        rubrics = cls.findall(".//{*}Rubric")
        for r in rubrics:
            if r.attrib.get("kind") == "preferred":
                label = r.find(".//{*}Label")
                if label is not None:
                    title = label.text

        # Definition
        for r in rubrics:
            if r.attrib.get("kind") == "definition":
                label = r.find(".//{*}Label")
                if label is not None:
                    definition = label.text

        # Meta fields
        meta = {m.attrib["name"]: m.attrib["value"]
                for m in cls.findall(".//{*}Meta")}

        para295 = meta.get("Para295")
        para301 = meta.get("Para301")
        sex_code = meta.get("SexCode")
        age_low = meta.get("AgeLow")
        age_high = meta.get("AgeHigh")
        infectious = meta.get("Infectious") == "J"
        content = meta.get("Content") == "J"

        # We collect items instead of immediately embedding
        cur.execute("""
            INSERT INTO icd_class (
                code, kind, title, definition,
                para295, para301, sex_code,
                age_low, age_high, infectious, content
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (code) DO UPDATE SET title = EXCLUDED.title, definition = EXCLUDED.definition;
        """, (
            code, kind, title, definition,
            para295, para301, sex_code,
            age_low, age_high, infectious, content
        ))
        
    print("Classes inserted. Now batch-generating embeddings for titles...")
    
    # Fetch all inserted items that need title embeddings
    cur.execute("SELECT code, title FROM icd_class WHERE title IS NOT NULL")
    all_classes = cur.fetchall()
    
    batch_size = 500
    for i in tqdm(range(0, len(all_classes), batch_size), desc="Embedding XML Titles"):
        batch = all_classes[i:i+batch_size]
        codes = [row[0] for row in batch]
        texts = [f"{row[0]} {row[1]}" for row in batch]
        
        embeddings = generate_embeddings_batch(texts)
        
        for code, emb in zip(codes, embeddings):
            cur.execute("""
                INSERT INTO icd_embedding (
                    icd_code, source_type, embedding
                )
                VALUES (%s,%s,%s);
            """, (code, "title", emb))

    print("XML import complete.")


# --------------------------------------------------
# Import Alphabetical TXT
# --------------------------------------------------

def import_txt():
    print("Loading valid ICD codes...")
    cur.execute("SELECT code FROM icd_class;")
    valid_codes = {row[0] for row in cur.fetchall()}

    print("Parsing Alphabetical TXT...")

    with open(TXT_FILE, encoding="utf-8") as f:
        synonym_batch = []
        for line in tqdm(f, desc="Parsing Synonyms TXT"):
            parts = line.strip().split("|")

            if len(parts) != 8:
                continue

            coding_type = int(parts[0])
            code = parts[3]
            term = parts[7]

            if not code or not term:
                continue
                
            # Clean up the code (remove trailing '+' and '*')
            code = code.rstrip('+*')

            if code not in valid_codes:
                continue
                
            synonym_batch.append((code, term, coding_type))
            
    print(f"Extracted {len(synonym_batch)} synonyms. Starting batch insertion and embedding...")
    
    batch_size = 500
    for i in tqdm(range(0, len(synonym_batch), batch_size), desc="Embedding Synonyms"):
        batch = synonym_batch[i:i+batch_size]
        
        # 1. Insert the synonyms into Postgres to get IDs
        inserted_items = []
        for (code, term, coding_type) in batch:
            cur.execute("""
                INSERT INTO icd_synonym (icd_code, term, coding_type)
                VALUES (%s,%s,%s)
                RETURNING id;
            """, (code, term, coding_type))
            synonym_id = cur.fetchone()[0]
            inserted_items.append((code, synonym_id, term))
            
        # 2. Batch generate embeddings
        texts = [item[2] for item in inserted_items]
        embeddings = generate_embeddings_batch(texts)
        
        # 3. Insert embeddings
        for (code, synonym_id, _), emb in zip(inserted_items, embeddings):
            cur.execute("""
                INSERT INTO icd_embedding (
                    icd_code, source_type, source_id, embedding
                )
                VALUES (%s,%s,%s,%s);
            """, (code, "synonym", synonym_id, emb))

    print("TXT import complete.")


# --------------------------------------------------
# Main
# --------------------------------------------------

if __name__ == "__main__":
    create_tables()
    import_xml()
    import_txt()

    cur.close()
    conn.close()

    print("Full ICD import finished successfully.")