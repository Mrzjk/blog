from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.api.v1.api import api_router
from app.core.config import settings
from app.database import engine, Base

from app.models import user, post, social, game
import os

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)

    if engine.url.get_backend_name() == "sqlite":
        with engine.begin() as conn:
            user_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(users)"))]
            if "last_active" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN last_active DATETIME"))
            if "birthday" not in user_columns:
                conn.execute(text("ALTER TABLE users ADD COLUMN birthday DATETIME"))
                
            post_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(posts)"))]
            if "category_id" not in post_columns:
                conn.execute(text("ALTER TABLE posts ADD COLUMN category_id INTEGER REFERENCES categories(id)"))
            if "status" not in post_columns:
                conn.execute(text("ALTER TABLE posts ADD COLUMN status VARCHAR(20) DEFAULT 'published'"))
                
            msg_columns = [row[1] for row in conn.execute(text("PRAGMA table_info(messages)"))]
            if "message_type" not in msg_columns:
                conn.execute(text("ALTER TABLE messages ADD COLUMN message_type VARCHAR(20) DEFAULT 'text'"))
            if "deleted_by_sender" not in msg_columns:
                conn.execute(text("ALTER TABLE messages ADD COLUMN deleted_by_sender BOOLEAN DEFAULT 0"))
            if "deleted_by_receiver" not in msg_columns:
                conn.execute(text("ALTER TABLE messages ADD COLUMN deleted_by_receiver BOOLEAN DEFAULT 0"))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
def read_root():
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}
