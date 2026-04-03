"""
services/db_service.py

Description: Handles all database connections and raw SQL queries
             for the application using a connection pool.
"""

# Third-party — Database
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

# Internal
from config import DB_HOST, DB_NAME, DB_PASSWORD, DB_USER


class DatabaseService:
    """
    Provides managed database connections and data access methods.
    Uses psycopg2.pool.SimpleConnectionPool to improve performance.

    The pool is lazily initialized on first use so that Docker startup
    race conditions (DB not yet ready) do not permanently disable the pool.
    """
    def __init__(self):
        self.pool = None  # Pool is created lazily on first request

    def _ensure_pool(self):
        """
        Creates the connection pool if it does not yet exist.
        Called lazily by get_connection() so Docker startup ordering issues
        cannot permanently break the pool.
        """
        if self.pool:
            return
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                1, 20,
                host=DB_HOST,
                database=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD
            )
            print("PostgreSQL connection pool created successfully.")
        except Exception as e:
            print(f"Error creating connection pool (will retry on next request): {e}")
            self.pool = None

    def close(self):
        """Closes all connections in the pool gracefully."""
        if self.pool:
            self.pool.closeall()
            self.pool = None
            print("PostgreSQL connection pool closed.")

    @contextmanager
    def get_connection(self):
        """
        Context manager for acquiring and releasing a connection from the pool.
        Lazily initializes the pool on first use.
        """
        self._ensure_pool()

        if not self.pool:
            yield None
            return

        conn = self.pool.getconn()
        try:
            yield conn
        finally:
            self.pool.putconn(conn)


    def get_subcodes_from_db(self, code: str) -> tuple:
        """
        Fetches the parent title and all subcodes for a given 3-digit ICD-10 code.
        """
        with self.get_connection() as conn:
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

    def get_cached_chat(self, code: str, prompt_type: str) -> str:
        """Looks up a cached AI response for a given ICD code and prompt type."""
        with self.get_connection() as conn:
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
                cur.close()

    def save_cached_chat(self, code: str, prompt_type: str, ans: str):
        """Saves an AI-generated response to the cache table."""
        if not ans or ans.startswith("Error") or ans.startswith("Gemini API key"):
            return

        with self.get_connection() as conn:
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
                cur.close()

    def get_cached_conditions_from_db(self) -> list:
        with self.get_connection() as conn:
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

    def get_sitemap_codes(self) -> list:
        """Fetches all ICD codes that have been cached, for sitemap generation."""
        with self.get_connection() as conn:
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

    def run_vector_search_query(self, embedding: list, limit: int) -> list:
        """Executes a pgvector similarity search against the ICD embedding table."""
        with self.get_connection() as conn:
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

    def get_icd_code_direct(self, code: str) -> tuple | None:
        """Fetches a single ICD-10 entry by exact 3-digit code match."""
        with self.get_connection() as conn:
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