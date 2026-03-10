import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

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
DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "medcode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "changeme")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel('gemini-2.5-flash')
else:
    print("WARNING: GEMINI_API_KEY is not set.")

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

# --- Data Models (JSON Structure) ---
class DiagnosticRequest(BaseModel):
    user_input: str
    top_k: int = 5

class SourceData(BaseModel):
    icd_code: str
    title: str
    term: str
    similarity: float

class VectorSearchResponse(BaseModel):
    user_input: str
    neighbors: List[SourceData]

class FinalResponse(BaseModel):
    llm_answer: str
    sources: List[SourceData]

# --- Endpoints ---

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Medcode Backend is running"}

@app.post("/api/diagnose", response_model=FinalResponse)
def diagnose(request: DiagnosticRequest):
    """
    1. Receives JSON from frontend (user_input).
    2. Performs vector search.
    3. Builds Prompt & calls Gemini API.
    4. Returns JSON to frontend.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        
        # 1. Generate embedding for user input
        query_embedding = embedding_model.encode(request.user_input).tolist()
        
        # 2. Vector Search (Cosine Similarity -> <=> operator in pgvector)
        # We join with icd_class to get the title, and check icd_synonym if the source was a synonym
        query = """
            SELECT 
                e.icd_code, 
                c.title,
                CASE 
                    WHEN e.source_type = 'synonym' THEN s.term 
                    ELSE c.title 
                END as term,
                1 - (e.embedding <=> %s::vector) as similarity
            FROM icd_embedding e
            JOIN icd_class c ON e.icd_code = c.code
            LEFT JOIN icd_synonym s ON e.source_id = s.id AND e.source_type = 'synonym'
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s;
        """
        cur.execute(query, (query_embedding, query_embedding, request.top_k))
        results = cur.fetchall()
        
        # Structure the intermediate JSON containing top K neighbors and user input
        neighbors = []
        for row in results:
            neighbors.append(SourceData(
                icd_code=row[0],
                title=row[1] or "",
                term=row[2] or "",
                similarity=row[3]
            ))
            
        intermediate_data = VectorSearchResponse(
            user_input=request.user_input,
            neighbors=neighbors
        )
        
        # 3. PROMPT ENGINEERING SECTION
        # Hier ist dein Bereich als Prompt Engineer!
        # Baue aus intermediate_data einen guten Prompt für Gemini.
        
        context_text = "\n".join([f"- {n.icd_code}: {n.term} (Ähnlichkeit: {n.similarity:.2f})" for n in intermediate_data.neighbors])
        
        prompt = f"""
Du bist ein hilfreicher medizinischer Kodier-Assistent. 
Ein Arzt hat folgende Diagnose/Symptome eingegeben: "{intermediate_data.user_input}"

Die Vektordatenbank hat folgende relevanten ICD-10 Codes gefunden:
{context_text}

Bitte analysiere die Eingabe und die gefundenen Codes. Welcher Code passt am besten?
Begründe deine Entscheidung kurz und prägnant. Antworte in einem sauberen, professionellen Ton.
"""
        
        # 4. API Call to Gemini
        llm_answer = "Gemini API key is missing. Prompt was generated but not sent."
        if GEMINI_API_KEY:
            try:
                response = llm_model.generate_content(prompt)
                llm_answer = response.text
            except Exception as e:
                llm_answer = f"Error calling Gemini API: {e}"

        # 5. Return JSON to formatting back to frontend
        return FinalResponse(
            llm_answer=llm_answer,
            sources=intermediate_data.neighbors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conn:
            cur.close()
            conn.close()

# Temporary Endpoint if you only want to test the vector search outputs
@app.post("/api/search", response_model=VectorSearchResponse)
def search_only(request: DiagnosticRequest):
    """
    Returns only the intermediate JSON (Vector Search results).
    Good for testing the embeddings before sending to LLM.
    """
    conn = get_db_connection()
    if not conn:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    try:
        cur = conn.cursor()
        query_embedding = embedding_model.encode(request.user_input).tolist()
        
        query = """
            SELECT 
                e.icd_code, 
                c.title,
                CASE 
                    WHEN e.source_type = 'synonym' THEN s.term 
                    ELSE c.title 
                END as term,
                1 - (e.embedding <=> %s::vector) as similarity
            FROM icd_embedding e
            JOIN icd_class c ON e.icd_code = c.code
            LEFT JOIN icd_synonym s ON e.source_id = s.id AND e.source_type = 'synonym'
            ORDER BY e.embedding <=> %s::vector
            LIMIT %s;
        """
        cur.execute(query, (query_embedding, query_embedding, request.top_k))
        results = cur.fetchall()
        
        neighbors = []
        for row in results:
            neighbors.append(SourceData(
                icd_code=row[0],
                title=row[1] or "",
                term=row[2] or "",
                similarity=row[3]
            ))
            
        return VectorSearchResponse(
            user_input=request.user_input,
            neighbors=neighbors
        )
    finally:
        if conn:
            cur.close()
            conn.close()
