"""
dependencies.py

Description: Configures and provides Service singletons for FastAPI Dependency Injection.
"""

from services.db_service import DatabaseService
from services.chat_service import ChatService
from services.search_service import SearchService
from config import genai_client, meili_index

# Initialize singletons for the application
db_service = DatabaseService()
chat_service = ChatService(db_service=db_service, genai_client=genai_client)
search_service = SearchService(
    db_service=db_service,
    chat_service=chat_service,
    meili_index=meili_index,
    use_parallel=False # to delete
)

def get_db_service() -> DatabaseService:
    return db_service

def get_chat_service() -> ChatService:
    return chat_service

def get_search_service() -> SearchService:
    return search_service
