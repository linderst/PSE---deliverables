"""
services/db_service.py

Description: Handles all database connections and raw SQL queries
             for the application. All other services should use
             get_db_connection() from this module.
"""

# Third-party — Database
import psycopg2

# Internal
from medical_synonyms import expand_query
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER

# --- Database Connection ---
def get_db_connection():
    """
    Creates and returns the PostgreSQL database connection.

    Uses the globally configured database credentials (DB_HOST, DB_NAME,
    DB_USER, DB_PASSWORD) to establish the connection (from the .env file).

    Returns:
        psycopg2.connection: An active database connection object if
            successful, or None if the connection attempt fails.
    
        Raises:
            psycopg2.OperationalError: If the database connection fails due to
        wrong credentials, unreachable host, or database not existing.
    """
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None
    
def get_subcodes_from_db(code: str) -> tuple:
    """
    Fetches the parent title and all subcodes for a given 3-digit ICD-10 code.

    Args:
        code (str): A 3-digit ICD-10 code. Example: "I21"

    Returns:
        tuple: A pair of (parent_title, rows) where:
            - parent_title (str): Title of the parent code.
            - rows (list): Raw database rows, each containing
                (code, title, is_leaf, synonym_count).
        Returns (code, []) if the database connection fails.

    Raises:
        psycopg2.DatabaseError: If the SQL query fails.
    """
    conn = get_db_connection()
    if not conn:
        return (code, [])

    try:
        cur = conn.cursor()

        # Get parent title
        cur.execute("SELECT title FROM icd_class WHERE code = %s", (code,))
        parent_row = cur.fetchone()
        parent_title = parent_row[0] if parent_row else code

        # Get all subcodes (4+ digits) with their synonym count
        cur.execute("""
            SELECT
                c.code,
                c.title,
                c.is_leaf,
                COUNT(s.id) AS synonym_count
            FROM icd_class c
            LEFT JOIN icd_synonym s ON s.icd_code = c.code
            WHERE c.code LIKE %s
            GROUP BY c.code, c.title, c.is_leaf
            ORDER BY synonym_count DESC, c.code ASC
        """, (f"{code}.%",))

        return (parent_title, cur.fetchall())

    finally:
        cur.close()
        conn.close() 

def get_cached_chat(code: str, prompt_type: str) -> str:
    """
    Looks up a cached AI response for a given ICD code and prompt type.

    Args:
        code (str): The ICD-10 code to look up. Example: "I21"
        prompt_type (str): The category of the cached response.
            Example: "explain", "specialist", "guidance"

    Returns:
        str: The cached response text if found.
        None: If no cache entry exists or the connection fails.

    Raises:
        psycopg2.DatabaseError: If the SQL query fails.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT response_text FROM icd_ai_cache WHERE icd_code = %s AND prompt_type = %s",
            (code, prompt_type)
        )
        row = cur.fetchone()
        if row:
            print(f"Cache hit: returned {prompt_type} for {code}")
            return row[0]
        return None
    except Exception as e:
        print(f"[cache-error] reading {e}")
        return None
    finally:
        conn.close()

def save_cached_chat(code: str, prompt_type: str, ans: str):
    """
    Saves an AI-generated response to the cache table.

    Skips saving if the response is empty or contains an error message.
    Uses ON CONFLICT DO NOTHING to avoid overwriting existing cache entries.

    Args:
        code (str): The ICD-10 code to cache the response for. Example: "I21"
        prompt_type (str): The category of the response being cached.
            Example: "explain", "specialist", "guidance"
        ans (str): The AI-generated response text to cache.

    Returns:
        None
    
    Raises:
        psycopg2.DatabaseError: If the SQL query fails.
    """
    if ans and not ans.startswith("Error") and not ans.startswith("Gemini API key"):
        conn = get_db_connection()
        if not conn:
            return
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO icd_ai_cache (icd_code, prompt_type, response_text) 
                VALUES (%s, %s, %s) 
                ON CONFLICT (icd_code, prompt_type) DO NOTHING
            """, (code, prompt_type, ans))
            conn.commit()
            print(f"[cache-miss] saved {prompt_type} for {code}")
        except Exception as e:
            print(f"[cache-error] writing {e}")
            conn.rollback()
        finally:
            conn.close()


def get_cached_conditions_from_db() -> list:
    
    conn = get_db_connection()
    if not conn:
        return []
    
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.code, c.title
            FROM icd_class c
            JOIN icd_ai_cache a ON c.code = a.icd_code
            ORDER BY c.title ASC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()
    

def get_sitemap_codes() -> list:
    """
    Fetches all ICD codes that have been cached, for sitemap generation.

    Returns:
        list: Raw rows of (code, title) tuples ordered by code ascending.
            Returns an empty list if the database connection fails.
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT c.code, c.title
            FROM icd_class c
            JOIN icd_ai_cache a ON c.code = a.icd_code
            ORDER BY c.code ASC
        """)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def run_vector_search_query(embedding: list, limit: int) -> list:
    """
    Executes a pgvector similarity search against the ICD embedding table.
    """
    
    conn = get_db_connection()

    if not conn:
        return []
    try:
        cur = conn.cursor()
        sql = """
            WITH raw_matches AS (
                SELECT
                    SUBSTRING(e.icd_code, 1, 3) AS three_digit_code,
                    1 - (e.embedding <=> %s::vector) AS similarity
                FROM icd_embedding e
                ORDER BY e.embedding <=> %s::vector
                LIMIT 200
            ),
            ranked_categories AS (
                SELECT
                    three_digit_code,
                    0.6 * MAX(similarity) + 0.4 * AVG(similarity) AS combined_score
                FROM raw_matches
                GROUP BY three_digit_code
                ORDER BY combined_score DESC
                LIMIT %s
            )
            SELECT
                r.three_digit_code,
                COALESCE(c.title, r.three_digit_code) AS final_title,
                r.combined_score
            FROM ranked_categories r
            LEFT JOIN icd_class c ON c.code = r.three_digit_code
            ORDER BY r.combined_score DESC;
        """
        cur.execute(sql, (embedding, embedding, limit))
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()

def get_icd_code_direct(code: str) -> tuple | None:
    """
    Fetches a single ICD-10 entry by exact 3-digit code match.
    Used for direct code recognition when the user types e.g. "R51".

    Args:
        code (str): A 3-digit ICD-10 code. Example: "R51"

    Returns:
        tuple: A (code, title) pair if found.
        None: If no match exists or the connection fails.

    Raises:
        psycopg2.DatabaseError: If the SQL query fails.
    """
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT code, title FROM icd_class WHERE code = %s LIMIT 1",
            (code,)
        )
        return cur.fetchone()
    finally:
        cur.close()
        conn.close()