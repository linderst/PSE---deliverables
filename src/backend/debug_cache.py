import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")

print("Testing Cache Insertion Error...")
try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()
    
    # Check if table exists
    try:
        cur.execute("SELECT * FROM icd_ai_cache LIMIT 1")
        print("Table icd_ai_cache exists. Columns:", [desc[0] for desc in cur.description])
        conn.rollback()  # reset state after potential error
    except Exception as e:
        print("Table check error:", e)
        conn.rollback()

    # Try inserting valid data
    try:
        ans = "Test Response"
        prompt_type = "explain"
        code = "I10"
        
        cur.execute("""
            INSERT INTO icd_ai_cache (icd_code, prompt_type, response_text) 
            VALUES (%s, %s, %s) 
            ON CONFLICT (icd_code, prompt_type) DO NOTHING
        """, (code, prompt_type, ans))
        conn.commit()
        print("Test insertion succeeded!")
    except Exception as e:
        print("Test insertion failed snippet:", type(e).__name__)
        print(e)
        conn.rollback()

    cur.close()
    conn.close()
except Exception as e:
    print(f"Connection error: {e}")
