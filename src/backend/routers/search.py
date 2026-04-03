"""
routers/search.py

Description: Defines all HTTP endpoints related to ICD-10 search.
             Delegates all business logic to search_service.py.
"""

# Third-party — Web framework
from fastapi import APIRouter, Depends
from typing import Annotated

# Internal
from models import SearchResponse
from dependencies import get_search_service
from services.search_service import SearchService

router = APIRouter()

@router.get("/api/search", response_model=SearchResponse)
def search_diagnoses(
    q: str, 
    limit: int = 5,
    search_service: Annotated[SearchService, Depends(get_search_service)] = None
):
    """
    Hybrid search:
    1. Direct ICD code recognition (e.g. 'R51' → score 1.0)
    2. Meilisearch (fast, typo-tolerant, synonym-aware) — PRIMARY
    3. pgvector fallback if Meilisearch is unavailable
    """
    return search_service.perform_search(q, limit)

@router.get("/api/search/refined", response_model=SearchResponse)
def search_refined(
    q: str, 
    limit: int = 5,
    search_service: Annotated[SearchService, Depends(get_search_service)] = None
):
    """
    Gemini-enhanced search:
    1. Ask Gemini to extract 5 medical ICD-10 terms from the plain-language query
    2. Run vector search with those terms
    This endpoint is called in parallel with the fast /api/search — the frontend
    shows instant results from /api/search and quietly upgrades them if /api/search/refined
    returns a meaningfully different top result.
    """
    return search_service.perform_refined_search(q, limit)