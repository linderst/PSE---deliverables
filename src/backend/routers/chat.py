"""
routers/search.py

Description: Defines all HTTP endpoints related to ICD-10 search.
             Delegates all business logic to chat_service.py.
"""

from fastapi import APIRouter, Depends
from typing import Annotated

# Internal
from models import ChatRequest, ChatResponse, ContextualChatRequest
from dependencies import get_chat_service
from services.chat_service import ChatService

router = APIRouter()

@router.post("/api/chat/explain", response_model=ChatResponse)
def chat_explain(
    req: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)]
):
    prompt = "Erkläre die folgende medizinische Diagnose verständlich für einen Laien in maximal 3-4 Sätzen:\nDiagnose: {question}\nAntworte professionell und empathisch."
    return chat_service.handle_cached_chat(req, "explain", prompt, disclaimer=True)

@router.post("/api/chat/specialist", response_model=ChatResponse)
def chat_specialist(
    req: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)]
):
    prompt = "Welcher Facharzt oder Spezialist ist für die Diagnose '{question}' zuständig und wann sollte man diesen aufsuchen?\nAntworte kurz und prägnant in 2-3 Sätzen."
    return chat_service.handle_cached_chat(req, "specialist", prompt)

@router.post("/api/chat/guidance", response_model=ChatResponse)
def chat_guidance(
    req: ChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)]
):
    prompt = "Was sind die gängigen Behandlungsmethoden oder erste ärztliche Schritte bei der Diagnose '{question}'?\nAntworte in 3-4 Sätzen übersichtlich. Erwähne, dass dies keinen Arztbesuch ersetzt."
    return chat_service.handle_cached_chat(req, "guidance", prompt)


@router.post("/api/chat/contextual", response_model=ChatResponse)
def chat_contextual(
    req: ContextualChatRequest,
    chat_service: Annotated[ChatService, Depends(get_chat_service)]
):
    prompt = f"Im Kontext der Diagnose '{req.condition_code}: {req.condition_title}', beantworte folgende Frage des Patienten kurz, hilfreich und laienverständlich:\nFrage des Patienten: {req.question}"
    ans = chat_service.ask_gemini(prompt)
    return ChatResponse(answer=ans)