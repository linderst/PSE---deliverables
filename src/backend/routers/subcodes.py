"""
routers/subcodes.py

Description: Defines all HTTP endpoints related to subcodes.
             Delegates all business logic to search_service.py.
"""
# Standard library
import os
import re

# Third-party — Web framework
from fastapi import APIRouter, Depends, HTTPException
from typing import Annotated

# Internal
from models import SubcodeResponse, SubcodeResult
from dependencies import get_db_service
from services.db_service import DatabaseService

router = APIRouter()

@router.get("/api/subcodes", response_model=SubcodeResponse)
def get_subcodes(
    code: str,
    db_service: Annotated[DatabaseService, Depends(get_db_service)]
):
    """
    Returns all 4-digit ICD-10 codes under a given 3-digit parent code.
    Sorted by synonym_count DESC (= proxy for clinical frequency/relevance).
    """
    code = code.strip().upper()[:3]

    parent_title, rows = db_service.get_subcodes_from_db(code)

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