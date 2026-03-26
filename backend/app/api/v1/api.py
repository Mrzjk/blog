from fastapi import APIRouter
from app.api.v1 import auth, posts, chat, categories, games

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(posts.router, prefix="/posts", tags=["posts"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
api_router.include_router(games.router, prefix="/games", tags=["games"])