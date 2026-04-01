# Third-party — Data validation
from pydantic import BaseModel

# Third-party — Type hints
from typing import List, Dict, Any, Optional

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