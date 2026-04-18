"""
    services/search_service.py

    Description: Handles ICD-10 Search functionality by utilizing
                 Meilisearch, pgvector, and Google Gemini APIs.
"""
# Standard library
import os
import re

# Internal
from models import SearchResponse, SearchResult
from medical_synonyms import expand_query
from services.db_service import DatabaseService
from services.chat_service import ChatService

class SearchService:
    """
    SearchService coordinates queries between direct code matching,
    Meilisearch typo-tolerant searching, and pgvector semantic searching.
    """
    def __init__(self, db_service: DatabaseService, chat_service: ChatService, genai_client, meili_index):
        self.db = db_service
        self.chat_service = chat_service
        self.genai_client = genai_client
        self.meili_index = meili_index

    def _get_gemini_embedding(self, text: str) -> list[float]:
        """Generate embedding using Google Gemini API instead of local model."""
        if not self.genai_client:
            return []
        import time
        max_retries = 3

        for attempt in range(max_retries):
            try:
                resp = self.genai_client.models.embed_content(
                    model="gemini-embedding-001",
                    contents=text,
                    config={"task_type": "RETRIEVAL_QUERY"}
                )
                return resp.embeddings[0].values
            except Exception as e:
                print(f"Error generating embedding (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return []

    def _run_vector_search(self, q_text: str, limit: int) -> list[SearchResult]:
        """
        Embeds a query and runs a combined-score vector search against ICD codes.
        """
        expanded = expand_query(q_text)
        embedding = self._get_gemini_embedding(expanded)

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

    def perform_search(self, q: str, limit: int = 5) -> SearchResponse:
        """
        Hybrid search:
        1. Direct ICD code recognition (e.g. 'R51' → score 1.0)
        2. Meilisearch (fast, typo-tolerant, synonym-aware) — PRIMARY
        3. pgvector fallback if Meilisearch is unavailable
        """
        q = q.lower().strip()
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

        # ── 2. Try Meilisearch ───────────────────────────────────────────────────
        if self.meili_index is not None:
            try:
                search_result = self.meili_index.search(q, {
                    "limit": limit * 5,   # fetch more candidates to account for deduplication
                    "attributesToRetrieve": ["code", "title"],
                    "showRankingScore": True
                })
                hits = search_result.get("hits", [])
                if hits:
                    seen = {}
                    for hit in hits:
                        code_full = hit["code"]
                        code3 = code_full[:3]
                        raw_score = hit.get("_rankingScore", 0.5)

                        # Subcodes (e.g. O24.1) are penalised by 15% so that the
                        # 3-digit parent code wins when both appear in results.
                        # Without this, O24.1 "Diabetes Typ 2 in der Schwangerschaft"
                        # would beat E11 "Diabetes mellitus Typ 2" for the query
                        # "diabetes typ 2" because it contains more matching words.
                        is_parent_code = len(code_full) == 3
                        effective_score = raw_score if is_parent_code else raw_score * 0.85

                        # Keep the best effective score per 3-digit group
                        if code3 not in seen or effective_score > seen[code3].score:
                            seen[code3] = SearchResult(
                                code=code3,
                                title=hit.get("title") or "Unbekannte Diagnose",
                                score=round(effective_score, 3)
                            )

                    # Sort by effective score (best first) and apply limit
                    sorted_results = sorted(seen.values(), key=lambda r: r.score, reverse=True)[:limit]

                    if sorted_results:
                        best_match = sorted_results[0]
                        if best_match.score >= 0.75:
                            print(f"[meili] '{q}' → {[r.code for r in sorted_results]}")
                            filtered_results = [r for r in sorted_results if r.score >= 0.75]
                            return SearchResponse(results=filtered_results)
                        else:
                            print(f"[meili] Top score {best_match.score} < 0.75, falling back to pgvector")
            except Exception as e:
                print(f"[meili] Error, falling back to vector search: {e}")

        # ── 3. pgvector fallback ─────────────────────────────────────────────────
        results = self._run_vector_search(q, limit)
        return SearchResponse(results=results)

    def perform_refined_search(self, q: str, limit: int = 5) -> SearchResponse:
        """
        Gemini-enhanced search:
        1. Ask Gemini to extract 5 medical ICD-10 terms from the plain-language query
        2. Run vector search with those terms
        """
        q = q.lower().strip()
        if not q:
            return SearchResponse(results=[])

        try:
            prompt = (
                f"Du bist ein medizinischer Kodierassistent für ICD-10. "
                f"Extrahiere aus der Symptombeschreibung des Nutzers 5 passende medizinische Fachbegriffe oder ICD-10-Termini.\n\n"
                f"Beispiele:\n"
                f"Eingabe: \"Kopfschmerz mit Fieber\"\n"
                f"Antwort: Influenza, Grippaler Infekt, COVID-19, Sinusitis, Rhinitis\n\n"
                f"Eingabe: \"Rückenschmerzen\"\n"
                f"Antwort: Dorsalgie, Lumbago, Spondylose, Bandscheibenbeschwerden, Myalgie\n\n"
                f"Eingabe: \"{q}\"\n"
                f"Antwort: "
            )
            gemini_response = self.chat_service.ask_gemini(prompt, temperature=0.0)

            if gemini_response.startswith("Error") or not gemini_response.strip() or gemini_response.startswith("Gemini API key") or gemini_response.startswith("Entschuldigung"):
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
                                    score=min(score, 0.80)  # Cap refined results at 80% (lowered from 90%)
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
            for r in results:
                r.score = min(r.score, 0.80)  # Cap refined results at 80%
            return SearchResponse(results=results[:limit])

        finally:
            pass