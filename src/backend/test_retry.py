import sys
import os

sys.path.insert(0, os.path.abspath('.'))

from services.chat_service import ChatService
from models import ChatRequest

class MockModels:
    def generate_content(self, model, contents):
        print("Mock: generate_content aufgerufen! Wir simulieren einen 502 Server Fehler.")
        raise Exception("502 Server Overloaded")

class MockClient:
    def __init__(self):
        self.models = MockModels()

class MockDB:
    def get_cached_chat(self, code, prompt_type):
        return None
    def save_cached_chat(self, code, prompt_type, ans):
        pass

def main():
    print("Starte Retry-Test fuer ChatService...\n")
    import time
    
    chat_svc = ChatService(db_service=MockDB(), genai_client=MockClient())
    
    start = time.time()
    req = ChatRequest(question="I10: Essentielle Hypertonie")
    
    print("-> Sende Anfrage an Gemini...", flush=True)
    res = chat_svc.handle_cached_chat(req, "explain", "Erklaere: {question}")
    
    duration = time.time() - start
    print(f"\n<- Fertig in {duration:.2f} Sekunden.")
    print(f"<- Finale Antwort vom Service:\n'{res.answer}'\n")

if __name__ == "__main__":
    main()
