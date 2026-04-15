"""
services/chat_service.py

Description: Handles interactions with the Google Gemini API,
             including response caching to avoid redundant API calls.
"""
# Third-party — Type hints
from typing import List, Dict, Any, Optional

# Internal
from models import ChatRequest, ChatResponse
from services.db_service import DatabaseService

class ChatService:
    """
    Service for generating AI responses and managing answer caches
    via the Gemini API.
    """
    def __init__(self, db_service: DatabaseService, genai_client):
        self.db_service = db_service
        self.genai_client = genai_client

    def ask_gemini(self, prompt: str) -> str:
        """
        Returns LLM-generated (gemini) answer based on input string (prompt).
        """
        if not self.genai_client:
            return "Gemini API key is missing. Cannot generate response."
        import time
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.genai_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                return response.text
            except Exception as e:
                print(f"Error calling Gemini API (Attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)  # Warte 2 Sekunden vor dem nächsten Versuch
                else:
                    return "Entschuldigung, die KI-Server sind aktuell überlastet. Bitte versuche es später erneut."

    def handle_cached_chat(self, req: ChatRequest, prompt_type: str, prompt_template: str, disclaimer: bool = False) -> ChatResponse:
        """
        Handles a chat request by checking the cache first, then calling
        Gemini if no cached response exists. Saves new responses to cache.
        """
        # 1. Extract code "I10: Essentielle..." -> "I10"
        code = req.question.split(":")[0].strip()[:10]
        
        # 2. Check Cache
        cached = self.db_service.get_cached_chat(code, prompt_type)
        if cached:
            return ChatResponse(answer=cached, disclaimer=disclaimer)

        # 3. No cache hit -> Ask Gemini
        prompt = prompt_template.format(question=req.question)
        ans = self.ask_gemini(prompt)

        # 4. Save to Cache
        self.db_service.save_cached_chat(code, prompt_type, ans)
        
        return ChatResponse(answer=ans, disclaimer=disclaimer)