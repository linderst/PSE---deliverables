import os
import psycopg2
from lxml import etree
from sentence_transformers import SentenceTransformer
import numpy as np
from tqdm import tqdm
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables
# --------------------------------------------------

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

#for production use: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2" adjust dimenstion to 768
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

DATA_DIR = os.getenv("DATA_DIR", ".")
XML_FILE = os.path.join(DATA_DIR, "icd10gm2026syst_claml_20250912.xml")
TXT_FILE = os.path.join(DATA_DIR, "icd10gm2026alpha_edvtxt_20250926.txt")

EMBEDDING_MODEL = "text-embedding-3-small"
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

    cur.execute("""
    CREATE INDEX IF NOT EXISTS idx_embedding
    ON icd_embedding
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);
    """)

    print("Tables created.")


# --------------------------------------------------
# Embedding Function
# --------------------------------------------------

def generate_embedding(text: str):
    embedding = model.encode(text)
    return embedding.tolist()


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

        cur.execute("""
            INSERT INTO icd_class (
                code, kind, title, definition,
                para295, para301, sex_code,
                age_low, age_high, infectious, content
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (code) DO NOTHING;
        """, (
            code, kind, title, definition,
            para295, para301, sex_code,
            age_low, age_high, infectious, content
        ))

        # Generate embedding for title
        if title:
            embedding = generate_embedding(f"{code} {title}")

            cur.execute("""
                INSERT INTO icd_embedding (
                    icd_code, source_type, embedding
                )
                VALUES (%s,%s,%s);
            """, (code, "title", embedding))

    print("XML import complete.")


# --------------------------------------------------
# Import Alphabetical TXT
# --------------------------------------------------

def import_txt():
    print("Parsing Alphabetical TXT...")

    with open(TXT_FILE, encoding="utf-8") as f:
        for line in tqdm(f):
            parts = line.strip().split("|")

            if len(parts) != 8:
                continue

            coding_type = int(parts[0])
            code = parts[3]
            term = parts[7]

            if not code or not term:
                continue

            cur.execute("""
                INSERT INTO icd_synonym (icd_code, term, coding_type)
                VALUES (%s,%s,%s)
                RETURNING id;
            """, (code, term, coding_type))

            synonym_id = cur.fetchone()[0]

            embedding = generate_embedding(term)

            cur.execute("""
                INSERT INTO icd_embedding (
                    icd_code, source_type, source_id, embedding
                )
                VALUES (%s,%s,%s,%s);
            """, (code, "synonym", synonym_id, embedding))

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