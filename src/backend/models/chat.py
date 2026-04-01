# Third-party — Data validation
from pydantic import BaseModel

# Third-party — Type hints
from typing import List, Dict, Any, Optional

class ChatRequest(BaseModel):
    """
    Request body schema for a general chat query.

    Attributes:
        question (str): The medical term searched by the user.

    Example:
        {
            "question": "Herzinfarkt"
        }
    """
    question: str

class ContextualChatRequest(BaseModel):
    """
    Request body schema for a contextual chat query.

    Represents the data a client must send when asking a question
    in the context of a specific ICD-10 diagnosis. FastAPI uses this
    model to automatically validate and parse the incoming JSON body.

    Attributes:
        question (str): The medical question asked by the user.
        condition_code (str): The ICD-10 code for the diagnosis context.
        condition_title (str): The human-readable name of the diagnosis.

    Example:
        {
            "question": "What are the common treatment options?",
            "condition_code": "I21",
            "condition_title": "Acute myocardial infarction"
        }
    """
    question: str
    condition_code: str
    condition_title: str

class ChatResponse(BaseModel):
    """
    Response body schema for a general chat query.

    Wraps the AI-generated answer to a user's medical question,
    along with a flag indicating whether a medical disclaimer
    should be displayed in the frontend.

    Attributes:
        answer (str): The AI-generated response to the user's question.
        disclaimer (bool): If True, the frontend should display a disclaimer
            warning the user to consult a medical professional.
            Defaults to False.

    Example:
        {
            "answer": "Type 1 diabetes is an autoimmune condition where...",
            "disclaimer": True
        }
    """
    answer: str
    disclaimer: bool = False