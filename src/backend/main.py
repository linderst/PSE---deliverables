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
from dependencies import db_service
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # db_service establishes connection pool on startup
    yield
    # Cleanup DB connection pool gracefully
    db_service.close()

app = FastAPI(title="Medcode API", lifespan=lifespan)

# CORS: configurable via env var.
# Production: CORS_ORIGINS=https://med.qm1.ch (set in docker-compose.yml)
# Development: CORS_ORIGINS=* (set in docker-compose.override.yml)
cors_origins = os.getenv("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
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