"""
main.py

Description: Entry Point - Handles the logic of the website setup, 
             search algorithm and the answer generation/retrival.
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
from routers import search as search_router, chat as chat_router, subcodes as subcodes_router
from routers import seo_cache as seo_router

app = FastAPI(title="Medcode API")

# Setup CORS so the frontend can communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, this should be restricted
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include HTTPS Points from routers/
app.include_router(search_router.router)
app.include_router(chat_router.router)
app.include_router(subcodes_router.router)
app.include_router(seo_router.router)

# --- Endpoints ---
@app.get("/")
def read_root():
    return {"status": "ok", "message": "Medcode Backend is running"}