# Third-party — Data validation
from pydantic import BaseModel

# Third-party — Type hints
from typing import List, Dict, Any, Optional

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