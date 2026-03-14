import os
import re
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
from medical_synonyms import expand_query
import meilisearch

app = FastAPI(title="Medcode API")

# Setup CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("WARNING: GEMINI_API_KEY is not set.")

# Load Meilisearch config
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_KEY = os.getenv("MEILI_KEY", "masterKey")
try:
    meili_client = meilisearch.Client(MEILI_URL, MEILI_KEY)
    meili_index = meili_client.index("icd10")
    print(f"Meilisearch connected at {MEILI_URL}")
except Exception as e:
    meili_index = None
    print(f"WARNING: Meilisearch not available: {e}")

# Initialize Embedding Model (Must match the one in import_icd.py)
print("Loading Embedding Model...")
embedding_model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
print("Model loaded.")

# --- Database Connection ---
def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

# --- Data Models ---
class SearchResult(BaseModel):
    code: str
    title: str
    score: float = 0.0
    version: str = "2024"

class SearchResponse(BaseModel):
    results: List[SearchResult]

class ChatRequest(BaseModel):
    question: str

class ContextualChatRequest(BaseModel):
    question: str
    condition_code: str
    condition_title: str

class ChatResponse(BaseModel):
    answer: str
    disclaimer: bool = False

class SubcodeResult(BaseModel):
    code: str
    title: str
    synonym_count: int = 0
    is_leaf: Optional[bool] = None

class SubcodeResponse(BaseModel):
    parent_code: str
    parent_title: str
    subcodes: List[SubcodeResult]

# --- Helper ---
def ask_gemini(prompt: str) -> str:
    if not GEMINI_API_KEY:
        return "Gemini API key is missing. Cannot generate response."
    try:
        response = llm_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Medcode Backend is running"}

@app.get("/api/subcodes", response_model=SubcodeResponse)
def get_subcodes(code: str):
    """
    Returns all 4-digit ICD-10 codes under a given 3-digit parent code.
    Sorted by synonym_count DESC (= proxy for clinical frequency/relevance).
    """
    code = code.strip().upper()[:3]

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        cur = conn.cursor()

        # Get parent title
        cur.execute("SELECT title FROM icd_class WHERE code = %s", (code,))
        parent_row = cur.fetchone()
        parent_title = parent_row[0] if parent_row else code

        # Get all subcodes (4+ digits) with their synonym count
        cur.execute("""
            SELECT
                c.code,
                c.title,
                c.is_leaf,
                COUNT(s.id) AS synonym_count
            FROM icd_class c
            LEFT JOIN icd_synonym s ON s.icd_code = c.code
            WHERE c.code LIKE %s
            GROUP BY c.code, c.title, c.is_leaf
            ORDER BY synonym_count DESC, c.code ASC
        """, (f"{code}.%",))

        rows = cur.fetchall()
        subcodes = [
            SubcodeResult(
                code=row[0],
                title=row[1] or "Unbekannte Diagnose",
                is_leaf=row[2],
                synonym_count=row[3] or 0
            )
            for row in rows
        ]

        return SubcodeResponse(
            parent_code=code,
            parent_title=parent_title,
            subcodes=subcodes
        )
    finally:
        cur.close()
        conn.close()

@app.get("/api/search", response_model=SearchResponse)
def search_diagnoses(q: str, limit: int = 5):
    """
    Hybrid search:
    1. Direct ICD code recognition (e.g. 'R51' → score 1.0)
    2. Meilisearch (fast, typo-tolerant, synonym-aware) — PRIMARY
    3. pgvector fallback if Meilisearch is unavailable
    """
    q = q.strip()
    if not q:
        return SearchResponse(results=[])

    # ── 1. Direct ICD code detection ─────────────────────────────────────────
    icd_pattern = re.compile(r'^[A-Z]\d{2}(\.\d+)?$', re.IGNORECASE)
    if icd_pattern.match(q):
        three_digit = q[:3].upper()
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT code, title FROM icd_class WHERE code = %s LIMIT 1", (three_digit,))
                row = cur.fetchone()
                if row:
                    return SearchResponse(results=[
                        SearchResult(code=row[0], title=row[1] or "Unbekannte Diagnose", score=1.0)
                    ])
            finally:
                cur.close()
                conn.close()

    # ── 2. Try Meilisearch ───────────────────────────────────────────────────
    if meili_index is not None:
        try:
            # Meilisearch handles typos, synonyms, and German morphology natively
            search_result = meili_index.search(q, {
                "limit": limit * 3,   # get more candidates to deduplicate by 3-digit code
                "attributesToRetrieve": ["code", "title"],
                "showRankingScore": True
            })
            hits = search_result.get("hits", [])
            if hits:
                # Deduplicate by 3-digit code
                seen = {}
                for hit in hits:
                    code3 = hit["code"][:3]
                    if code3 not in seen:
                        # Use actual Meilisearch ranking score (0.0 to 1.0)
                        # Only perfect exact matches will get 1.0. Typos/partial matches get less.
                        raw_score = hit.get("_rankingScore", 0.5)
                        
                        seen[code3] = SearchResult(
                            code=code3,
                            title=hit.get("title") or "Unbekannte Diagnose",
                            score=round(raw_score, 3)
                        )
                    if len(seen) >= limit:
                        break

                if seen:
                    print(f"[meili] '{q}' → {[r.code for r in seen.values()]}")
                    return SearchResponse(results=list(seen.values()))
        except Exception as e:
            print(f"[meili] Error, falling back to vector search: {e}")

    # ── 3. pgvector fallback ─────────────────────────────────────────────────
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        expanded_q = expand_query(q)
        query_embedding = embedding_model.encode(expanded_q).tolist()

        sql = """
            WITH raw_matches AS (
                SELECT
                    SUBSTRING(e.icd_code, 1, 3) AS three_digit_code,
                    1 - (e.embedding <=> %s::vector) AS similarity
                FROM icd_embedding e
                ORDER BY e.embedding <=> %s::vector
                LIMIT 200
            ),
            ranked_categories AS (
                SELECT
                    three_digit_code,
                    0.6 * MAX(similarity) + 0.4 * AVG(similarity) AS combined_score
                FROM raw_matches
                GROUP BY three_digit_code
                ORDER BY combined_score DESC
                LIMIT %s
            )
            SELECT
                r.three_digit_code,
                COALESCE(c.title, r.three_digit_code) AS final_title,
                r.combined_score
            FROM ranked_categories r
            LEFT JOIN icd_class c ON c.code = r.three_digit_code
            ORDER BY r.combined_score DESC;
        """
        cur = conn.cursor()
        cur.execute(sql, (query_embedding, query_embedding, limit))
        rows = cur.fetchall()
        out = [
            SearchResult(code=r[0], title=r[1] or "Unbekannte Diagnose", score=float(r[2]) if r[2] else 0.0)
            for r in rows
        ]
        return SearchResponse(results=out[:limit])

    finally:
        if conn:
            cur.close()
            conn.close()


def _run_vector_search(q_text: str, limit: int, conn) -> list[SearchResult]:
    """
    Shared helper: embed q_text and run the combined-score vector search.
    Returns a list of SearchResult objects.
    """
    cur = conn.cursor()
    try:
        # Expand with local synonym dict first
        expanded = expand_query(q_text)
        embedding = embedding_model.encode(expanded).tolist()

        sql = """
            WITH raw_matches AS (
                SELECT
                    SUBSTRING(e.icd_code, 1, 3) AS three_digit_code,
                    1 - (e.embedding <=> %s::vector) AS similarity
                FROM icd_embedding e
                ORDER BY e.embedding <=> %s::vector
                LIMIT 200
            ),
            ranked_categories AS (
                SELECT
                    three_digit_code,
                    0.6 * MAX(similarity) + 0.4 * AVG(similarity) AS combined_score
                FROM raw_matches
                GROUP BY three_digit_code
                ORDER BY combined_score DESC
                LIMIT %s
            )
            SELECT
                r.three_digit_code,
                COALESCE(c.title, r.three_digit_code) AS final_title,
                r.combined_score
            FROM ranked_categories r
            LEFT JOIN icd_class c ON c.code = r.three_digit_code
            ORDER BY r.combined_score DESC;
        """
        cur.execute(sql, (embedding, embedding, limit))
        rows = cur.fetchall()
        return [
            SearchResult(
                code=row[0],
                title=row[1] or "Unbekannte Diagnose",
                score=float(row[2]) if row[2] is not None else 0.0
            )
            for row in rows
        ]
    finally:
        cur.close()


@app.get("/api/search/refined", response_model=SearchResponse)
def search_refined(q: str, limit: int = 5):
    """
    Gemini-enhanced search:
    1. Ask Gemini to extract 5 medical ICD-10 terms from the plain-language query
    2. Run vector search with those terms
    This endpoint is called in parallel with the fast /api/search — the frontend
    shows instant results from /api/search and quietly upgrades them if /api/search/refined
    returns a meaningfully different top result.
    """
    q = q.strip()
    if not q:
        return SearchResponse(results=[])

    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        # Step 1: Gemini extracts medical terminology from the plain-language input
        prompt = (
            f"Du bist ein medizinischer Kodierassistent für ICD-10. "
            f"Der Nutzer hat folgende Symptome oder Beschwerden beschrieben: \"{q}\"\n"
            f"Gib mir genau 5 medizinische Fachbegriffe oder ICD-10-Diagnosen, die am besten passen. "
            f"Antworte NUR mit den 5 Begriffen, durch Komma getrennt, ohne Erklärung. Auf Deutsch."
        )
        gemini_response = ask_gemini(prompt)

        # If Gemini failed or returned an error, fall back to plain search
        if gemini_response.startswith("Error") or not gemini_response.strip():
            results = _run_vector_search(q, limit, conn)
            return SearchResponse(results=results[:limit])

        # Combine original query + Gemini terms for maximum recall
        expanded_query = q + " " + gemini_response.strip()
        print(f"[refined] Original: '{q}' → Gemini expanded: '{gemini_response.strip()}'")

        results = _run_vector_search(expanded_query, limit, conn)
        return SearchResponse(results=results[:limit])

    finally:
        if conn:
            conn.close()



@app.post("/api/chat/explain", response_model=ChatResponse)
def chat_explain(req: ChatRequest):
    prompt = f"Erkläre die folgende medizinische Diagnose verständlich für einen Laien in maximal 3-4 Sätzen:\nDiagnose: {req.question}\nAntworte professionell und empathisch."
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans, disclaimer=True)

@app.post("/api/chat/specialist", response_model=ChatResponse)
def chat_specialist(req: ChatRequest):
    prompt = f"Welcher Facharzt oder Spezialist ist für die Diagnose '{req.question}' zuständig und wann sollte man diesen aufsuchen?\nAntworte kurz und prägnant in 2-3 Sätzen."
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans)

@app.post("/api/chat/guidance", response_model=ChatResponse)
def chat_guidance(req: ChatRequest):
    prompt = f"Was sind die gängigen Behandlungsmethoden oder erste ärztliche Schritte bei der Diagnose '{req.question}'?\nAntworte in 3-4 Sätzen übersichtlich. Erwähne, dass dies keinen Arztbesuch ersetzt."
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans)

@app.post("/api/chat/contextual", response_model=ChatResponse)
def chat_contextual(req: ContextualChatRequest):
    prompt = f"Im Kontext der Diagnose '{req.condition_code}: {req.condition_title}', beantworte folgende Frage des Patienten kurz, hilfreich und laienverständlich:\nFrage des Patienten: {req.question}"
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans)
