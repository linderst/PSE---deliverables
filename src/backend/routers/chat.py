"""
routers/search.py

Description: Defines all HTTP endpoints related to ICD-10 search.
             Delegates all business logic to chat_service.py.
"""

# Third-party — Web framework
from fastapi import APIRouter

# Internal
from models import ChatRequest, ChatResponse, ContextualChatRequest
from services.chat_service import handle_cached_chat, ask_gemini

router = APIRouter()

@router.post("/api/chat/explain", response_model=ChatResponse)
def chat_explain(req: ChatRequest):
    prompt = "Erkläre die folgende medizinische Diagnose verständlich für einen Laien in maximal 3-4 Sätzen:\nDiagnose: {question}\nAntworte professionell und empathisch."
    return handle_cached_chat(req, "explain", prompt, disclaimer=True)

@router.post("/api/chat/specialist", response_model=ChatResponse)
def chat_specialist(req: ChatRequest):
    prompt = "Welcher Facharzt oder Spezialist ist für die Diagnose '{question}' zuständig und wann sollte man diesen aufsuchen?\nAntworte kurz und prägnant in 2-3 Sätzen."
    return handle_cached_chat(req, "specialist", prompt)

@router.post("/api/chat/guidance", response_model=ChatResponse)
def chat_guidance(req: ChatRequest):
    prompt = "Was sind die gängigen Behandlungsmethoden oder erste ärztliche Schritte bei der Diagnose '{question}'?\nAntworte in 3-4 Sätzen übersichtlich. Erwähne, dass dies keinen Arztbesuch ersetzt."
    return handle_cached_chat(req, "guidance", prompt)


@router.post("/api/chat/contextual", response_model=ChatResponse)
def chat_contextual(req: ContextualChatRequest):
    prompt = f"Im Kontext der Diagnose '{req.condition_code}: {req.condition_title}', beantworte folgende Frage des Patienten kurz, hilfreich und laienverständlich:\nFrage des Patienten: {req.question}"
    ans = ask_gemini(prompt)
    return ChatResponse(answer=ans)