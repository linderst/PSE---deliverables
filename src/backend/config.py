"""
config.py

Description: Loads environment variables from the .env file and exposes
             them as constants for use across the application. All
             environment-specific configuration belongs here — no other
             file should call os.getenv() directly.
"""

# Standard library
import os

# Third-party — AI / Google
from google import genai

# Third-party — Search
import meilisearch

# Third-party
from dotenv import load_dotenv

load_dotenv()  # reads your .env file


# Load database configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Initialize Gemini
genai_client = None
if GEMINI_API_KEY:
    genai_client = genai.Client(api_key=GEMINI_API_KEY)
else:
    print("WARNING: GEMINI_API_KEY is not set.")

# Load Meilisearch config
MEILI_URL = os.getenv("MEILI_URL", "http://localhost:7700")
MEILI_KEY = os.getenv("MEILI_KEY", "masterKey")
try:
    meili_client = meilisearch.Client(MEILI_URL, MEILI_KEY)
    meili_index = meili_client.index("icd10")
    print(f"Meilisearch connected at {MEILI_URL}")
except Exception as e:
    meili_index = None
    print(f"WARNING: Meilisearch not available: {e}")