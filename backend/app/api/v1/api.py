from fastapi import APIRouter
from app.api.v1 import auth, posts, chat

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])