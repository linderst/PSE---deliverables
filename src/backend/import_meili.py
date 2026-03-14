"""
import_meili.py

Imports all ICD-10 codes and their synonyms from PostgreSQL into Meilisearch.
Run once (or after DB updates) with:
    docker compose --profile import run meili-importer

What gets indexed per document:
  - code: "R51"
  - title: "Kopfschmerz"
  - synonyms: aggregated from icd_synonym table
  - search_text: combined field — what Meilisearch searches against
  - kind: category type from icd_class
"""

import os
import psycopg2
import meilisearch
from tqdm import tqdm
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "medcode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_KEY = os.getenv("MEILI_KEY", "masterKey")

INDEX_NAME = "icd10"

# ── Meilisearch synonyms for colloquial German ─────────────────────────────
# These are loaded ONCE via API and permanently stored in Meilisearch.
SYNONYMS = {
    "bluthochdruck": ["hypertonie", "arterielle hypertonie", "hochdruck", "I10"],
    "hochdruck": ["hypertonie", "arterielle hypertonie", "bluthochdruck"],
    "herzrasen": ["tachykardie", "palpitationen", "herzrhythmusstörung", "arrhythmie"],
    "herzstolpern": ["arrhythmie", "extrasystolen", "herzrhythmusstörung"],
    "herzinfarkt": ["myokardinfarkt", "akutes koronarsyndrom"],
    "herzanfall": ["myokardinfarkt", "akutes koronarsyndrom"],
    "schlaganfall": ["apoplex", "hirninfarkt", "zerebrovaskulärer insult", "I63", "I64"],
    "zuckerkrankheit": ["diabetes mellitus", "hyperglykämie", "E11"],
    "ohnmacht": ["synkope", "kollaps", "bewusstlosigkeit"],
    "schwindel": ["vertigo", "benommenheit", "H81"],
    # Kopfschmerz ≠ Migräne — deliberately separated
    "kopfschmerzen": ["kopfschmerz", "cephalalgie", "R51"],
    "kopfschmerz": ["cephalalgie", "R51"],
    "migräne": ["hemikranie", "G43"],
    "rückenschmerzen": ["rückenschmerz", "dorsalgie", "lumbago", "lumbalgie", "M54"],
    "rückenschmerz": ["dorsalgie", "lumbago", "M54"],
    "kreuzschmerzen": ["lumbago", "lumbalgie", "lws-syndrom"],
    "schilddrüsenunterfunktion": ["hypothyreose", "myxödem", "E03"],
    "schilddrüsenüberfunktion": ["hyperthyreose", "thyreotoxikose", "E05"],
    "asthma": ["asthma bronchiale", "atemwegsobstruktion", "J45"],
    "lungenentzündung": ["pneumonie", "J18"],
    "erkältung": ["rhinitis", "nasopharyngitis", "J00"],
    "grippe": ["influenza", "J09", "J11"],
    "verstopfung": ["obstipation", "konstipation", "K59"],
    "sodbrennen": ["reflux", "gerd", "pyrosis", "K21"],
    "magengeschwür": ["ulcus ventriculi", "magenulkus", "K25"],
    "harnwegsinfekt": ["harnwegsinfektion", "zystitis", "N30"],
    "blasenentzündung": ["zystitis", "urethritis", "harnwegsinfektion"],
    "nierensteine": ["nephrolithiasis", "urolithiasis", "N20"],
    "bandscheibenvorfall": ["bandscheibenprolaps", "diskusprolaps", "M51"],
    "depression": ["depressive episode", "affektive störung", "F32", "F33"],
    "angst": ["angststörung", "panikattacke", "F40", "F41"],
    "schlaflosigkeit": ["insomnie", "schlafstörung", "G47"],
    "neurodermitis": ["atopische dermatitis", "atopisches ekzem", "L20"],
    "schuppenflechte": ["psoriasis", "L40"],
    "osteoporose": ["knochenschwund", "M81"],
    "gicht": ["arthritis urica", "hyperurikämie", "M10"],
    "arthrose": ["osteoarthrose", "gonarthrose", "coxarthrose", "M15", "M16", "M17"],
    "rheuma": ["rheumatoide arthritis", "M05", "M06"],
    "krebs": ["karzinom", "neoplasie", "maligne neubildung"],
    "corona": ["covid-19", "sars-cov-2", "U07"],
    "covid": ["covid-19", "sars-cov-2", "U07"],
    "tinnitus": ["ohrgeräusch", "H93"],
    "grauer star": ["katarakt", "linsentrübung", "H26"],
    "grüner star": ["glaukom", "H40"],
    "fettsucht": ["adipositas", "obesitas", "E66"],
    "übergewicht": ["adipositas", "E66"],
}



def main():
    # ── Connect to PostgreSQL ───────────────────────────────────────────────
    print("Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD
    )
    cur = conn.cursor()

    # ── Connect to Meilisearch ──────────────────────────────────────────────
    print(f"Connecting to Meilisearch at {MEILI_URL}...")
    client = meilisearch.Client(MEILI_URL, MEILI_KEY)

    # Create / get index
    try:
        client.create_index(INDEX_NAME, {"primaryKey": "code"})
    except Exception:
        pass  # Index already exists
    index = client.index(INDEX_NAME)

    # ── Configure index settings ─────────────────────────────────────────────
    print("Configuring index settings...")
    index.update_settings({
        "searchableAttributes": ["search_text", "title", "code"],
        "displayedAttributes": ["code", "title", "kind"],
        "rankingRules": [
            "words", "typo", "proximity", "attribute", "sort", "exactness"
        ],
        "typoTolerance": {
            "enabled": True,
            "minWordSizeForTypos": {"oneTypo": 5, "twoTypos": 8}
        },
        "synonyms": SYNONYMS,
    })

    # ── Fetch all 3-digit ICD classes ────────────────────────────────────────
    print("Fetching ICD-10 classes from PostgreSQL...")
    cur.execute("""
        SELECT code, title, kind 
        FROM icd_class 
        WHERE LENGTH(code) = 3
        ORDER BY code
    """)
    classes = cur.fetchall()
    print(f"  {len(classes)} 3-digit classes found")

    # ── Fetch all synonyms, group by 3-digit parent code ─────────────────────
    print("Fetching synonyms...")
    cur.execute("""
        SELECT SUBSTRING(icd_code, 1, 3) AS code3, term
        FROM icd_synonym
        WHERE icd_code IS NOT NULL
    """)
    from collections import defaultdict
    synonyms_by_code = defaultdict(list)
    for code3, term in cur.fetchall():
        synonyms_by_code[code3].append(term)
    print(f"  {sum(len(v) for v in synonyms_by_code.values())} synonym entries loaded")

    # ── Also include 4+ digit codes collapsed into parent ────────────────────
    cur.execute("""
        SELECT SUBSTRING(code, 1, 3) AS code3, title
        FROM icd_class
        WHERE LENGTH(code) > 3
        ORDER BY code
    """)
    child_titles_by_code = defaultdict(list)
    for code3, title in cur.fetchall():
        if title:
            child_titles_by_code[code3].append(title)

    # ── Build documents ───────────────────────────────────────────────────────
    print("Building Meilisearch documents...")
    documents = []
    for code, title, kind in tqdm(classes):
        synonyms = synonyms_by_code.get(code, [])
        child_titles = child_titles_by_code.get(code, [])

        # Combine everything into a single search_text field
        parts = [code, title or ""]
        parts += synonyms[:50]        # limit to avoid huge documents
        parts += child_titles[:30]    # sub-codes enrich the parent
        search_text = " ".join(p for p in parts if p)

        documents.append({
            "code": code,
            "title": title or "",
            "kind": kind or "",
            "search_text": search_text,
        })

    # ── Upload in batches ─────────────────────────────────────────────────────
    BATCH = 500
    print(f"Uploading {len(documents)} documents to Meilisearch in batches of {BATCH}...")
    for i in range(0, len(documents), BATCH):
        batch = documents[i:i + BATCH]
        index.add_documents(batch)

    print("✅ Meilisearch import complete!")
    print(f"   Index: {INDEX_NAME} | URL: {MEILI_URL}")

    cur.close()
    conn.close()


if __name__ == "__main__":
    main()
