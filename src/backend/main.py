import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "db")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "medcode")
DB_PASSWORD = os.getenv("DB_PASSWORD", "medcode")
DB_PORT = os.getenv("DB_PORT", "5432")

app = FastAPI(title="Medcode ICD-10 API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


@app.get("/health")
def health():
    return {"status": "ok"}
