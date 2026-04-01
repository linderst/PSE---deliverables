"""
    services/search_service.py

    Description: 
"""
# Standard library
import os
import re

# Internal
from models import SearchResponse, SearchResult, ChatRequest, ChatResponse, ContextualChatRequest
from models import SubcodeResponse, SubcodeResult
from services.db_service import run_vector_search_query, get_icd_code_direct
from services.chat_service import ask_gemini
from medical_synonyms import expand_query
from config import genai_client
from config import meili_index, meili_client


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

def _run_vector_search(q_text: str, limit: int, conn) -> list[SearchResult]:
    """
    Embeds a query and runs a combined-score vector search against ICD codes.
    """
    expanded = expand_query(q_text)
    embedding = _get_gemini_embedding(expanded)

    if not embedding:
        # TODO report/catch error!
        return []

    rows = run_vector_search_query(embedding, limit)
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

def perform_search(q: str, limit: int = 5):
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
        row = get_icd_code_direct(three_digit)
        if row:
            return SearchResponse(results=[
                SearchResult(code=row[0], title=row[1] or "Unbekannte Diagnose", score=1.0)
            ])

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
    results = _run_vector_search(q, limit)
    return SearchResponse(results=results)

def perform_refined_search(q: str, limit: int = 5):
    """
    Gemini-enhanced search:
    1. Ask Gemini to extract 5 medical ICD-10 terms from the plain-language query
    2. Run vector search with those terms
    This endpoint is called in parallel with the fast /api/search — the frontend
    shows instant results from /api/search and quietly upgrades them if /api/search/refined
    returns a meaningfully different top result.
    """
    #TODO refactor database part in this function as function to db_service.py
    ()
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