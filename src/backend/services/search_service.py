"""
    services/search_service.py

    Description: Handles ICD-10 Search functionality by utilizing
                 Meilisearch, pgvector, and Google Gemini APIs.
"""
# Standard library
import os
import re
import time

# Internal
from models import SearchResponse, SearchResult
from medical_synonyms import expand_query
from services.db_service import DatabaseService
from services.chat_service import ChatService

# parallel search service
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor

class SearchService:
    """
    SearchService coordinates queries between direct code matching,
    Meilisearch typo-tolerant searching, and pgvector semantic searching.
    """
    def __init__(self, db_service, chat_service, genai_client, meili_index, use_parallel: bool = False):
        self.db = db_service
        self.chat_service = chat_service
        self.genai_client = genai_client
        self.meili_index = meili_index
        self.use_parallel = use_parallel
        self.embedding_model = SentenceTransformer(
            "paraphrase-multilingual-MiniLM-L12-v2"
        )

    def _get_embedding(self, text: str) -> list[float]:
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            print(f"[embedding-error] {e}")
            return []

    def perform_search(self, q: str, limit: int = 5) -> SearchResponse:
        print(f"[SEARCH MODE] {'PARALLEL' if self.use_parallel else 'SERIAL'}")
        if self.use_parallel:
            return self._perform_parallel_search(q, limit)
        else:
            return self._perform_serial_search(q, limit)
        
    def _perform_parallel_search(self, q: str, limit: int = 5) -> SearchResponse:
        q = q.strip()
        if not q:
            return SearchResponse(results=[])

        # ── 1. Direct match bleibt gleich ─────────────────
        icd_pattern = re.compile(r'^[A-Z]\d{2}(\.\d+)?$', re.IGNORECASE)
        if icd_pattern.match(q):
            three_digit = q[:3].upper()
            row = self.db.get_icd_code_direct(three_digit)
            if row:
                return SearchResponse(results=[
                    SearchResult(code=row[0], title=row[1], score=1.0)
                ])

        # ── 2. PARALLEL SEARCH ────────────────────────────
        with ThreadPoolExecutor() as executor:
            meili_future = executor.submit(self._run_meili_search, q, limit)
            vector_future = executor.submit(self._run_vector_search, q, limit)

            meili_results = meili_future.result()
            vector_results = vector_future.result()

        # ── 3. MERGE ──────────────────────────────────────
        merged = self._merge_results(meili_results, vector_results, limit)

        print(f"[hybrid] '{q}' → {[r.code for r in merged]}")

        return SearchResponse(results=merged)
    
    def _merge_results(self, meili_results, vector_results, limit):
        combined = {}

        alpha = 0.6
        beta = 0.4

        for r in meili_results:
            combined[r.code] = {
                "title": r.title,
                "score": alpha * r.score
            }

        for r in vector_results:
            if r.code in combined:
                combined[r.code]["score"] += beta * r.score
            else:
                combined[r.code] = {
                    "title": r.title,
                    "score": beta * r.score
                }

        results = [
            SearchResult(
                code=code,
                title=data["title"],
                score=round(data["score"], 3)
            )
            for code, data in combined.items()
        ]

        return sorted(results, key=lambda x: x.score, reverse=True)[:limit]

    def _run_vector_search(self, q_text: str, limit: int) -> list[SearchResult]:
        """
        Embeds a query and runs a combined-score vector search against ICD codes.
        """
        expanded = expand_query(q_text)
        embedding = self._get_embedding(expanded)

        if not embedding:
            return []

        rows = self.db.run_vector_search_query(embedding, limit)
        out = []
        for row in rows:
            raw_sim = float(row[2]) if row[2] is not None else 0.0
            # Raw similarity threshold: 0.73 (previously effective threshold was 0.80, too strict).
            # We expose raw_sim directly as the score so the UI can display meaningful percentages.
            if raw_sim >= 0.73:
                out.append(SearchResult(
                    code=row[0],
                    title=row[1] or "Unbekannte Diagnose",
                    score=round(raw_sim, 3)
                ))
        out.sort(key=lambda x: x.score, reverse=True)
        return out


    def _run_meili_search(self, q: str, limit: int) -> list[SearchResult]:
        if self.meili_index is None:
            return []

        try:
            search_result = self.meili_index.search(q, {
                "limit": limit * 5,
                "attributesToRetrieve": ["code", "title"],
                "showRankingScore": True
            })

            hits = search_result.get("hits", [])
            if not hits:
                return []

            seen = {}
            for hit in hits:
                code_full = hit["code"]
                code3 = code_full[:3]
                raw_score = hit.get("_rankingScore", 0.5)

                is_parent_code = len(code_full) == 3
                effective_score = raw_score if is_parent_code else raw_score * 0.85

                if code3 not in seen or effective_score > seen[code3].score:
                    seen[code3] = SearchResult(
                        code=code3,
                        title=hit.get("title") or "Unbekannte Diagnose",
                        score=round(effective_score, 3)
                    )

            return sorted(seen.values(), key=lambda r: r.score, reverse=True)[:limit]

        except Exception as e:
            print(f"[meili] error: {e}")
            return []

    def _perform_serial_search(self, q: str, limit: int = 5) -> SearchResponse:
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
            row = self.db.get_icd_code_direct(three_digit)
            if row:
                return SearchResponse(results=[
                    SearchResult(code=row[0], title=row[1] or "Unbekannte Diagnose", score=1.0)
                ])

        self._run_meili_search(q, limit)

        results = self._run_vector_search(q, limit)
        return SearchResponse(results=results)
    

    def perform_refined_search(self, q: str, limit: int = 5) -> SearchResponse:
        """
        Gemini-enhanced search:
        1. Ask Gemini to extract 5 medical ICD-10 terms from the plain-language query
        2. Run vector search with those terms
        """
        q = q.strip()
        if not q:
            return SearchResponse(results=[])

        try:
            prompt = (
                f"Du bist ein medizinischer Kodierassistent für ICD-10. "
                f"Der Nutzer hat folgende Symptome oder Beschwerden beschrieben: \"{q}\"\n"
                f"Gib mir genau 5 medizinische Fachbegriffe oder ICD-10-Diagnosen, die am besten passen. "
                f"Antworte NUR mit den 5 Begriffen, durch Komma getrennt, ohne Erklärung. Auf Deutsch."
            )
            gemini_response = self.chat_service.ask_gemini(prompt)

            if gemini_response.startswith("Error") or not gemini_response.strip() or gemini_response.startswith("Gemini API key"):
                results = self._run_vector_search(q, limit)
                return SearchResponse(results=results[:limit])

            expanded_query = q + " " + gemini_response.strip()
            print(f"[refined] Original: '{q}' → Gemini expanded: '{gemini_response.strip()}'")

            terms = [t.strip() for t in gemini_response.split(",") if t.strip()]
            all_meili_hits = {}
            
            if self.meili_index is not None:
                for term in terms:
                    try:
                        ms_res = self.meili_index.search(term, {
                            "limit": 3,
                            "attributesToRetrieve": ["code", "title"],
                            "showRankingScore": True
                        })
                        hits = ms_res.get("hits", [])
                        for hit in hits:
                            code3 = hit["code"][:3]
                            score = round(hit.get("_rankingScore", 0.0), 3)
                            if code3 not in all_meili_hits or score > all_meili_hits[code3].score:
                                all_meili_hits[code3] = SearchResult(
                                    code=code3,
                                    title=hit.get("title") or "Unbekannte Diagnose",
                                    score=score
                                )
                    except Exception as e:
                        print(f"[refined-meili] Error searching term '{term}': {e}")
                
                if all_meili_hits:
                    sorted_hits = sorted(all_meili_hits.values(), key=lambda x: x.score, reverse=True)
                    best_match = sorted_hits[0]
                    if best_match.score >= 0.75:
                        print(f"[refined-meili] Strong match found for expert terms: {best_match.code} ({best_match.score})")
                        filtered_results = [r for r in sorted_hits if r.score >= 0.70]
                        return SearchResponse(results=filtered_results[:limit])

            results = self._run_vector_search(expanded_query, limit)
            return SearchResponse(results=results[:limit])

        finally:
            pass