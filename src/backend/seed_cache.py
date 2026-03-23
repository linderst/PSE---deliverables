import os
import psycopg2
import time
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "medcode")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
API_BASE = "http://localhost:8000/api"

print("Starte Cache-Seerder...")
print("Verbinde mit Datenbank...")

try:
    conn = psycopg2.connect(host=DB_HOST, database=DB_NAME, user=DB_USER, password=DB_PASSWORD)
    cur = conn.cursor()
    
    # Hole die 100 häufigsten/relevantesten 3-stelligen ICD Codes
    # (Anzahl der Synonyme als Proxy für Verbreitung)
    cur.execute("""
        SELECT c.code, c.title, COUNT(s.id) as syn_count
        FROM icd_class c
        LEFT JOIN icd_synonym s ON s.icd_code = c.code
        WHERE length(c.code) = 3
        GROUP BY c.code, c.title
        ORDER BY syn_count DESC
        LIMIT 100;
    """)
    top_codes = cur.fetchall()
    cur.close()
    conn.close()
    print(f"{len(top_codes)} häufigste Diagnosen gefunden. Starte API Crawl...")
except Exception as e:
    print(f"Datenbankfehler: {e}")
    exit(1)

# Gemini API Rate Limit beachten (free tier: 15 req/min -> 4 sec pro Request)
# Wir rufen 3 Endpunkte auf (explain, specialist, guidance), also 12 Sekunden pro Krankheit.
DELAY_BETWEEN_REQUESTS = 4.0 

for idx, row in enumerate(top_codes):
    code = row[0]
    title = row[1]
    question = f"{code}: {title}"
    
    print(f"\n[{idx+1}/100] Verarbeite {code} ({title})...")
    
    endpoints = ["/chat/explain", "/chat/specialist", "/chat/guidance"]
    for ep in endpoints:
        url = API_BASE + ep
        payload = {"question": question}
        
        try:
            # Sende Post-Request an das laufende eigene Docker Backend
            res = requests.post(url, json=payload)
            if res.status_code == 200:
                data = res.json()
                answer = data.get("answer", "")
                if answer.startswith("Error") or answer.startswith("Gemini API"):
                    print(f"  x {ep:17} fehlgeschlagen (API Error: Rate Limit oder Key)")
                else:
                    print(f"  ✓ {ep:17} erfolgreich im Cache")
            else:
                print(f"  x {ep:17} fehlgeschlagen ({res.status_code})")
        except Exception as e:
            print(f"  x {ep:17} Verbindungsfehler: {e}")
            
        # Warten um Google's Rate Limit (15 RPM) zuverlässig einzuhalten
        time.sleep(4.2)

print("\nSeeding abgeschlossen! Alle 100 Top-Krankheiten sind nun in der PostgreSQL Datenbank gesichert.")
