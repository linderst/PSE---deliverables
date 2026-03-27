import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

# A comprehensive list of layman terms, typos, and common symptoms
TEST_TERMS = [
    "Zahnschmerzen",
    "Herzinfarkt",
    "Bein gebrochen",
    "Blutkrebs",
    "Schwindel",
    "Blinddarmentzündung",
    "Mandelentzündung",
    "Hexenschuss",
    "Migräne",
    "Sonnenstich",
    "Bandscheibenvorfall",
    "Schnupfen und Husten",
    "Leistenbruch",
    "Kopfweh",
    "Bluthochdruck",
    "Kieferknacken",
    "Hämorrhoiden",
    "Schuppenflechte",
    "Diabetes Typ 2",
    "Kieferschmerzen", # Known fallback vector search winner
]

def run_evaluation():
    print("# Search Relevance Evaluation Report\\n")
    print("| Suchbegriff | Top Resultat (Code) | Diagnose-Titel | Score |")
    print("|-------------|---------------------|----------------|-------|")
    
    success_count = 0
    
    for term in TEST_TERMS:
        response = client.get(f"/api/search?q={term}&limit=3")
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results:
                top = results[0]
                code = top["code"]
                title = top["title"]
                score = top["score"]
                print(f"| **{term}** | `{code}` | {title} | {score} |")
                success_count += 1
            else:
                print(f"| **{term}** | ❌ (Keine) | - | - |")
        else:
            print(f"| **{term}** | ❌ ERROR | API HTTP {response.status_code} | - |")

    print(f"\\n**Zusammenfassung:** {success_count} von {len(TEST_TERMS)} Begriffen haben erfolgreiche Treffer geliefert.")

if __name__ == "__main__":
    run_evaluation()
