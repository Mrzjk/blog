import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Blog Social API"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置，改为 SQLite 方便本地测试
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./blog_social.db")
    
    # Redis 配置
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # JWT 配置
    SECRET_KEY: str = "YOUR_SUPER_SECRET_KEY_HERE_CHANGE_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days

    class Config:
        case_sensitive = True

settings = Settings()
