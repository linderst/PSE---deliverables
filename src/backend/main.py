"""
main.py

Description: Entry Point - Handles the logic of the website setup, search algorithm and the answer generation/retrival.
"""
# Standard library
import os
import re

# Third-party — Web framework
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

# Third-party — Type hints
from typing import List, Dict, Any, Optional

# Internal
from config import genai_client
from config import meili_index, meili_client
from medical_synonyms import expand_query
from models import SearchResult, SearchResponse # import models from models/search.py
from models import ChatRequest, ChatResponse, ContextualChatRequest # import models from models/chat.py
from models import SubcodeResponse, SubcodeResult # import models from models/subcodes.py
from services.db_service import get_db_connection, get_subcodes_from_db
from services.db_service import get_cached_conditions_from_db, get_sitemap_codes
from services.chat_service import ask_gemini, handle_cached_chat
from services.search_service import _get_gemini_embedding, _run_vector_search
from services.search_service import perform_search, perform_refined_search
#TODO from routers import search, chat, subcodes

app = FastAPI(title="Medcode API")

# Setup CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#TODO
#app.include_router(search.router)
#app.include_router(chat.router)
#app.include_router(subcodes.router)

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

    parent_title, rows = get_subcodes_from_db(code)

    if not rows:
        raise HTTPException(status_code=500, detail="Database connection failed")

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

@app.get("/api/search", response_model=SearchResponse)
def search_diagnoses(q: str, limit: int = 5):
    """
    Hybrid search:
    1. Direct ICD code recognition (e.g. 'R51' → score 1.0)
    2. Meilisearch (fast, typo-tolerant, synonym-aware) — PRIMARY
    3. pgvector fallback if Meilisearch is unavailable
    """
    return perform_search(q, limit)

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
    return perform_refined_search(q, limit)

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
    GET /api/cached-conditions

    Returns all unique ICD codes that have been cached along with their titles.
    Used for generating the landing page overview and sitemap.

    Returns:
        dict: A dictionary containing a list of condition objects with
            code and title fields.

    Raises:
        HTTPException 500: If the database connection fails.
    """
    rows = get_cached_conditions_from_db()

    if not rows:
        raise HTTPException(status_code=500, detail="Database connection failed")

    results = [
        {"code": row[0], "title": row[1] or "Unbekannte Diagnose"}
        for row in rows
    ]
    return {"conditions": results}

@app.get("/sitemap.xml")
def get_sitemap():
    """
    Generates a dynamic sitemap.xml for all cached diseases
    to improve Google / Search Engine indexing.
    """
    import datetime
    from fastapi import Response

    rows = get_sitemap_codes()
    if not rows:
        raise HTTPException(status_code=500, detail="Database connection failed")
        
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