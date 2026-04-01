"""
services/chat_service.py

Description: Handles interactions with the Google Gemini API,
             including response caching to avoid redundant API calls.
"""
# Third-party — Type hints
from typing import List, Dict, Any, Optional

# Internal
from config import genai_client
from models import ChatRequest, ChatResponse
from services.db_service import get_cached_chat, save_cached_chat

# --- Helper ---
def ask_gemini(prompt: str) -> str:
    """
    Returns LLM-generated (gemini) answer based on input string (promt).

    Args:
        prompt (str): Question or Prompt that should be answered by Gemini.

    Returns:
        str: Response text to answer prompt.
        If API key is missing, there's an error message.

    Example:
        promt = "Explain this medical condition to me."
        response.text = "This medical condition is commenly referred to ..."
    """
    if not genai_client:
        return "Gemini API key is missing. Cannot generate response."
    try:
        response = genai_client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {e}"

def handle_cached_chat(req: ChatRequest, prompt_type: str, prompt_template: str, disclaimer: bool = False) -> ChatResponse:
    """
    Handles a chat request by checking the cache first, then calling
    Gemini if no cached response exists. Saves new responses to cache.

    Args:
        req (ChatRequest): The incoming chat request containing the question.
        prompt_type (str): Category of the prompt, used as cache key.
            Example: "explain", "specialist", "guidance"
        prompt_template (str): Template string with {question} placeholder.
        disclaimer (bool): If True, response includes a medical disclaimer.
            Defaults to False.

    Returns:
        ChatResponse: The AI-generated or cached answer with disclaimer flag.
    """
    #return get_cached_chat(req, prompt_type, prompt_template, False)
        # 1. Extract code "I10: Essentielle..." -> "I10"
    code = req.question.split(":")[0].strip()[:10]
    
    # 2. Check Cache
    cached = get_cached_chat(code, prompt_type)
    if cached:
        return ChatResponse(answer=cached, disclaimer=disclaimer)

    # 3. No cache hit -> Ask Gemini
    prompt = prompt_template.format(question=req.question)
    ans = ask_gemini(prompt)

    # 4. Save to Cache
    save_cached_chat(code, prompt_type, ans)
    
    return ChatResponse(answer=ans, disclaimer=disclaimer)