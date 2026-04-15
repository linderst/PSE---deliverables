import sys
import os

# Add src/backend to pythonpath so we can import services
sys.path.insert(0, os.path.abspath('src/backend'))

from services.chat_service import ChatService

# Mock for generation
class MockModels:
    def generate_content(self, model, contents):
        print("Mock: generate_content aufgerufen! Wir simulieren einen 502 Fehler.")
        raise Exception("502 Server Overloaded")

    def embed_content(self, model, contents, config):
        print("Mock: embed_content aufgerufen! Wir simulieren einen 502 Fehler.")
        raise Exception("502 Server Overloaded")

class MockClient:
    def __init__(self):
        self.models = MockModels()

# Dummy db_service with get_cached_chat returning None to force API call
class MockDB:
    def get_cached_chat(self, code, prompt_type):
        return None
    def save_cached_chat(self, code, prompt_type, ans):
        pass

def main():
    print("Starte Retry-Test für ChatService...\n")
    import time
    
    chat_svc = ChatService(db_service=MockDB(), genai_client=MockClient())
    
    start = time.time()
    
    from models import ChatRequest
    req = ChatRequest(question="I10: Essentielle Hypertonie")
    
    print("-> Sende Anfrage an Gemini...", flush=True)
    res = chat_svc.handle_cached_chat(req, "explain", "Erkläre: {question}")
    
    duration = time.time() - start
    print(f"\n<- Fertig in {duration:.2f} Sekunden.")
    print(f"<- Finale Antwort vom Service:\n'{res.answer}'\n")

if __name__ == "__main__":
    main()
