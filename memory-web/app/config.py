from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    # Database
    MW_DATABASE_URL: str = Field(
        default="postgresql://postgres:%3FBooker78%21@localhost:5432/postgres"
    )
    MW_DB_SCHEMA: str = Field(default="memoryweb")

    # Redis / Celery
    MW_REDIS_URL: str = Field(default="redis://localhost:6379/1")
    MW_CELERY_BROKER_URL: str = Field(default="redis://localhost:6379/1")
    MW_CELERY_RESULT_BACKEND: str = Field(default="redis://localhost:6379/1")

    # Ollama
    MW_OLLAMA_BASE_URL: str = Field(default="http://localhost:11434")
    MW_OLLAMA_MODEL: str = Field(default="qwen2.5-coder:32b")

    # Embeddings
    MW_EMBED_MODEL: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    MW_EMBED_DIM: int = Field(default=384)

    # Server
    MW_PORT: int = Field(default=8100)

    # Source paths
    MW_SESSIONS_DIR: str = Field(
        default="C:/Users/techai/.claude/projects/C--Users-techai"
    )
    MW_SHARED_CHAT_DIR: str = Field(
        default="//192.168.12.132/home/rblake2320/ai-business/shared/chat"
    )
    MW_SQLITE_MEMORY_PATH: str = Field(
        default="C:/Users/techai/.claude/skills/self-learning/_knowledge-base/memory.db"
    )

    # Pipeline tuning
    MW_SEGMENT_MAX_MESSAGES: int = Field(default=20)
    MW_SEGMENT_GAP_MINUTES: int = Field(default=30)
    MW_BATCH_SIZE: int = Field(default=500)
    MW_EMBED_BATCH_SIZE: int = Field(default=64)

settings = Settings()
