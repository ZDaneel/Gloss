from fastapi import APIRouter

from app.api.v1.endpoints import paragraphs, chat, resources

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(paragraphs.router, prefix="/paragraphs", tags=["paragraphs"])
api_router.include_router(resources.router, prefix="/resources", tags=["resources"])
