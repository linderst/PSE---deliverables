
import os
import sys
from dotenv import load_dotenv
from google import genai
import time

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

def test_prompt(q, iterations=5, temperature=None):
    prompt = (
        f"Du bist ein medizinischer Kodierassistent für ICD-10. "
        f"Der Nutzer hat folgende Symptome oder Beschwerden beschrieben: \"{q}\"\n"
        f"Gib mir genau 5 medizinische Fachbegriffe oder ICD-10-Diagnosen, die am besten passen. "
        f"Antworte NUR mit den 5 Begriffen, durch Komma getrennt, ohne Erklärung. Auf Deutsch."
    )
    
    print(f"Testing query: '{q}' with temperature={temperature}")
    for i in range(iterations):
        config = {}
        if temperature is not None:
            config['temperature'] = temperature
            
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash', # Use available model
                contents=prompt,
                config=config
            )
            print(f"Run {i+1}: {response.text.strip()}")
        except Exception as e:
            print(f"Error: {e}")
        time.sleep(1)

if __name__ == "__main__":
    query = "kopfschmerz mit fieber"
    print("--- Default Temperature (approx 1.0) ---")
    test_prompt(query, iterations=5)
    print("\n--- Low Temperature (0.0) ---")
    test_prompt(query, iterations=5, temperature=0.0)
