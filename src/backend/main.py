"""
main.py

Description: Handles the logic of the website setup, search algorithm and the answer generation/retrival.
"""
# Standard library
import os
import re

# Third-party — Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Third-party — Data validation
from pydantic import BaseModel

# Third-party — Database
import psycopg2

# Third-party — AI / Google
from google import genai

# Third-party — Type hints
from typing import List, Dict, Any, Optional

# Third-party — Search
import meilisearch

# Internal
from medical_synonyms import expand_query

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
genai_client = None
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
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

# --- Database Connection ---
def get_db_connection():
    """
    Creates and returns the PostgreSQL database connection.

    Uses the globally configured database credentials (DB_HOST, DB_NAME,
    DB_USER, DB_PASSWORD) to establish the connection (from the .env file).

    Returns:
        psycopg2.connection: An active database connection object if
            successful, or None if the connection attempt fails.
        Exception error, if unsucessful.
    """
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
    """
    Represents a single ICD-10 search result entry.

    Attributes:
        code (str): The ICD-10 code for the diagnosis.
        title (str): The name of the diagnosis.
        score (float): Relevance score of the result, used for ranking.
        version (str): The ICD-10 version the code belongs to.

    Example:
        {
            "code": "I21",
            "title": "Acute myocardial infarction",
            "score": 0.94,
            "version": "2025"
        }
    """
    code: str
    title: str
    score: float = 0.0
    version: str = "2024"

class SearchResponse(BaseModel):
    """
    Response body schema for an ICD-10 search query.

    Wraps a list of SearchResult objects returned by the search
    endpoint. FastAPI uses this model to serialize the response
    into JSON automatically.

    Attributes:
        results (List[SearchResult]): Ordered list of matching ICD-10
            entries, ranked by relevance score descending.

    Example:
        {
            "results": [
                {
                    "code": "I21",
                    "title": "Acute myocardial infarction",
                    "score": 0.94,
                    "version": "2024"
                },
                {
                    "code": "I20",
                    "title": "Angina pectoris",
                    "score": 0.87,
                    "version": "2024"
                }
            ]
        }
    """
    results: List[SearchResult]

class ChatRequest(BaseModel):
    """
    Request body schema for a general chat query.

    Attributes:
        question (str): The medical term searched by the user.

    Example:
        {
            "question": "Herzinfarkt"
        }
    """
    question: str

class ContextualChatRequest(BaseModel):
    """
    Request body schema for a contextual chat query.

    Represents the data a client must send when asking a question
    in the context of a specific ICD-10 diagnosis. FastAPI uses this
    model to automatically validate and parse the incoming JSON body.

    Attributes:
        question (str): The medical question asked by the user.
        condition_code (str): The ICD-10 code for the diagnosis context.
        condition_title (str): The human-readable name of the diagnosis.

    Example:
        {
            "question": "What are the common treatment options?",
            "condition_code": "I21",
            "condition_title": "Acute myocardial infarction"
        }
    """
    question: str
    condition_code: str
    condition_title: str

class ChatResponse(BaseModel):
    """
    Response body schema for a general chat query.

    Wraps the AI-generated answer to a user's medical question,
    along with a flag indicating whether a medical disclaimer
    should be displayed in the frontend.

    Attributes:
        answer (str): The AI-generated response to the user's question.
        disclaimer (bool): If True, the frontend should display a disclaimer
            warning the user to consult a medical professional.
            Defaults to False.

    Example:
        {
            "answer": "Type 1 diabetes is an autoimmune condition where...",
            "disclaimer": True
        }
    """
    answer: str
    disclaimer: bool = False

class SubcodeResult(BaseModel):
    """
    Represents a single ICD-10 subcode entry under a parent code.

    Used to display the hierarchical breakdown of an ICD-10 code
    into its more specific child codes.

    Attributes:
        code (str): The ICD-10 subcode.
        title (str): The name of the subcode.
        synonym_count (int): Number of synonyms associated with this subcode.
        is_leaf (Optional[bool]): If True, this subcode has no further
            child codes beneath it. If False, further subcodes exist.
            None if this information is not available.
    Example:
        {
            "code": "I21.0",
            "title": "Acute transmural myocardial infarction of anterior wall",
            "synonym_count": 3,
            "is_leaf": True
        }
    """
    code: str
    title: str
    synonym_count: int = 0
    is_leaf: Optional[bool] = None

class SubcodeResponse(BaseModel):
    """
    Response body schema for an ICD-10 subcode lookup.

    Returns the parent diagnosis alongside all of its direct child
    subcodes, allowing the frontend to render the hierarchical
    structure of an ICD-10 code.

    Attributes:
        parent_code (str): The ICD-10 code of the parent diagnosis.
        parent_title (str): The human-readable name of the parent diagnosis.
        subcodes (List[SubcodeResult]): All direct child subcodes
            belonging to the parent code, ordered by code ascending.
    Example:
        {
            "parent_code": "I21",
            "parent_title": "Acute myocardial infarction",
            "subcodes": [
                {
                    "code": "I21.0",
                    "title": "Acute transmural myocardial infarction of anterior wall",
                    "synonym_count": 3,
                    "is_leaf": true
                },
                {
                    "code": "I21.1",
                    "title": "Acute transmural myocardial infarction of inferior wall",
                    "synonym_count": 2,
                    "is_leaf": true
                }
            ]
        }
    """
    
    parent_code: str
    parent_title: str
    subcodes: List[SubcodeResult]

# --- Helper ---
def ask_gemini(prompt: str) -> str:
     """
    Returns LLM-generated (gemini) answer based on input string (promt).

    Returns:
        Error message, if API key is missing
        response.text: The generated answer text.

    Example:
        promt = "Explain this medical condition to me."
        response.text = "This medical condition is commenly referred to ..."
    """
    if not genai_client:
        return "Gemini API key is missing. Cannot generate response."
    try:
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
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

def _get_gemini_embedding(text: str) -> list[float]:
    """Generate embedding using Google Gemini API instead of local model."""
    if not genai_client:
        return []
    resp = genai_client.models.embed_content(
        model="gemini-embedding-001",
        contents=text,
        config={"task_type": "RETRIEVAL_QUERY"}
    )
    return resp.embeddings[0].values

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
                    best_match = list(seen.values())[0]
                    if best_match.score >= 0.75:
                        print(f"[meili] '{q}' → {[r.code for r in seen.values()]}")
                        # Only return results that meet the 0.75 threshold
                        filtered_results = [r for r in seen.values() if r.score >= 0.75]
                        return SearchResponse(results=filtered_results)
                    else:
                        print(f"[meili] Top score {best_match.score} < 0.75, falling back to pgvector")
        except Exception as e:
            print(f"[meili] Error, falling back to vector search: {e}")


    # ── 3. pgvector fallback ─────────────────────────────────────────────────
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")

    try:
        expanded_q = expand_query(q)
        try:
            query_embedding = _get_gemini_embedding(expanded_q)
        except Exception as e:
            print(f"[vector-search] Embedding API error: {e}")
            return SearchResponse(results=[])

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
        out = []
        for r in rows:
            raw_sim = float(r[2]) if r[2] else 0.0
            # Scale vector score so 0.70 becomes 0% and 1.0 becomes 100%
            scaled_score = max(0.0, (raw_sim - 0.70) / 0.30)
            if scaled_score >= 0.15: # i.e. original similarity > 0.745
                out.append(SearchResult(code=r[0], title=r[1] or "Unbekannte Diagnose", score=round(scaled_score, 3)))
        
        # Sort by scaled score
        out.sort(key=lambda x: x.score, reverse=True)
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
        try:
            embedding = _get_gemini_embedding(expanded)
        except Exception as e:
            print(f"[vector-search] Embedding API error: {e}")
            return []

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
        out = []
        for row in rows:
            raw_sim = float(row[2]) if row[2] is not None else 0.0
            scaled_score = max(0.0, (raw_sim - 0.75) / 0.25)
            if scaled_score >= 0.20:
                out.append(SearchResult(
                    code=row[0],
                    title=row[1] or "Unbekannte Diagnose",
                    score=round(scaled_score, 3)
                ))
        out.sort(key=lambda x: x.score, reverse=True)
        return out
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

        # Step 2: Try Meilisearch with the extracted expert terms individually
        terms = [t.strip() for t in gemini_response.split(",") if t.strip()]
        all_meili_hits = {}
        
        if meili_index is not None:
            for term in terms:
                try:
                    ms_res = meili_index.search(term, {
                        "limit": 3,
                        "attributesToRetrieve": ["code", "title"],
                        "showRankingScore": True
                    })
                    hits = ms_res.get("hits", [])
                    for hit in hits:
                        code3 = hit["code"][:3]
                        score = round(hit.get("_rankingScore", 0.0), 3)
                        # Keep the highest score for a code across all terms
                        if code3 not in all_meili_hits or score > all_meili_hits[code3].score:
                            all_meili_hits[code3] = SearchResult(
                                code=code3,
                                title=hit.get("title") or "Unbekannte Diagnose",
                                score=score
                            )
                except Exception as e:
                    print(f"[refined-meili] Error searching term '{term}': {e}")
            
            if all_meili_hits:
                # Sort all hits by score
                sorted_hits = sorted(all_meili_hits.values(), key=lambda x: x.score, reverse=True)
                best_match = sorted_hits[0]
                
                # If we found a very confident exact match for any of the Gemini terms
                if best_match.score >= 0.75:
                    print(f"[refined-meili] Strong match found for expert terms: {best_match.code} ({best_match.score})")
                    filtered_results = [r for r in sorted_hits if r.score >= 0.70]
                    return SearchResponse(results=filtered_results[:limit])

        # Step 3: If Meilisearch didn't find a strong match, run the heavy vector search
        results = _run_vector_search(expanded_query, limit, conn)
        return SearchResponse(results=results[:limit])

    finally:
        if conn:
            conn.close()



def handle_cached_chat(req: ChatRequest, prompt_type: str, prompt_template: str, disclaimer: bool = False) -> ChatResponse:
    # 1. Extract code "I10: Essentielle..." -> "I10"
    code = req.question.split(":")[0].strip()[:10]
    
    # 2. Check Cache
    conn = get_db_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("SELECT response_text FROM icd_ai_cache WHERE icd_code = %s AND prompt_type = %s", (code, prompt_type))
            row = cur.fetchone()
            if row:
                print(f"[cache-hit] returned {prompt_type} for {code}")
                return ChatResponse(answer=row[0], disclaimer=disclaimer)
        except Exception as e:
            print(f"[cache-error] reading {e}")
        finally:
            conn.close()

    # 3. Ask Gemini
    prompt = prompt_template.format(question=req.question)
    ans = ask_gemini(prompt)

    # 4. Save to Cache
    if ans and not ans.startswith("Error") and not ans.startswith("Gemini API key"):
        conn = get_db_connection()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("""
                    INSERT INTO icd_ai_cache (icd_code, prompt_type, response_text) 
                    VALUES (%s, %s, %s) 
                    ON CONFLICT (icd_code, prompt_type) DO NOTHING
                """, (code, prompt_type, ans))
                conn.commit()
                print(f"[cache-miss] saved {prompt_type} for {code}")
            except Exception as e:
                print(f"[cache-error] writing {e}")
                conn.rollback()
            finally:
                conn.close()

    return ChatResponse(answer=ans, disclaimer=disclaimer)


@app.post("/api/chat/explain", response_model=ChatResponse)
def chat_explain(req: ChatRequest):
    prompt = "Erkläre die folgende medizinische Diagnose verständlich für einen Laien in maximal 3-4 Sätzen:\nDiagnose: {question}\nAntworte professionell und empathisch."
    return handle_cached_chat(req, "explain", prompt, disclaimer=True)

@app.post("/api/chat/specialist", response_model=ChatResponse)
def chat_specialist(req: ChatRequest):
    prompt = "Welcher Facharzt oder Spezialist ist für die Diagnose '{question}' zuständig und wann sollte man diesen aufsuchen?\nAntworte kurz und prägnant in 2-3 Sätzen."
    return handle_cached_chat(req, "specialist", prompt)

@app.post("/api/chat/guidance", response_model=ChatResponse)
def chat_guidance(req: ChatRequest):
    prompt = "Was sind die gängigen Behandlungsmethoden oder erste ärztliche Schritte bei der Diagnose '{question}'?\nAntworte in 3-4 Sätzen übersichtlich. Erwähne, dass dies keinen Arztbesuch ersetzt."
    return handle_cached_chat(req, "guidance", prompt)


@app.post("/api/chat/contextual", response_model=ChatResponse)
def chat_contextual(req: ContextualChatRequest):
    prompt = f"Im Kontext der Diagnose '{req.condition_code}: {req.condition_title}', beantworte folgende Frage des Patienten kurz, hilfreich und laienverständlich:\nFrage des Patienten: {req.question}"
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans)

# --- SEO & Cache Overview ---

@app.get("/api/cached-conditions")
def get_cached_conditions():
    """
    Returns all unique ICD codes that have been cached (seeded) along with their titles.
    Used for generating the landing page overview and sitemap.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.code, c.title
            FROM icd_class c
            JOIN icd_ai_cache a ON c.code = a.icd_code
            ORDER BY c.title ASC
        """)
        rows = cur.fetchall()
        
        results = [{"code": row[0], "title": row[1] or "Unbekannte Diagnose"} for row in rows]
        return {"conditions": results}
    finally:
        if conn:
            cur.close()
            conn.close()

@app.get("/sitemap.xml")
def get_sitemap():
    """
    Generates a dynamic sitemap.xml for all cached diseases
    to improve Google / Search Engine indexing.
    """
    import datetime
    from fastapi import Response
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.code, c.title
            FROM icd_class c
            JOIN icd_ai_cache a ON c.code = a.icd_code
            ORDER BY c.code ASC
        """)
        rows = cur.fetchall()
        
        # Simple slugify logic mirroring the frontend
        def slugify(text):
            if not text:
                return "diagnose"
            text = text.lower()
            text = re.sub(r'[^a-z0-9öäüß]+', '-', text) # basic german support
            text = text.replace('ö', 'oe').replace('ä', 'ae').replace('ü', 'ue').replace('ß', 'ss')
            text = re.sub(r'[^a-z0-9]+', '-', text)
            text = re.sub(r'(^-|-$)+', '', text)
            return text

        base_url = "https://medcode.ch"
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
        xml_urls = []
        xml_urls.append(f'''
    <url>
        <loc>{base_url}/</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>daily</changefreq>
        <priority>1.0</priority>
    </url>''')
        
        # Add all cached pages
        for row in rows:
            code = row[0]
            title = row[1] or ""
            slug = slugify(title)
            url = f"{base_url}/{slug}/{code}"
            
            xml_urls.append(f'''
    <url>
        <loc>{url}</loc>
        <lastmod>{date_str}</lastmod>
        <changefreq>weekly</changefreq>
        <priority>0.8</priority>
    </url>''')
            
        xml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{''.join(xml_urls)}
</urlset>'''

        return Response(content=xml_content, media_type="application/xml")
        
    finally:
        if conn:
            cur.close()
            conn.close()
