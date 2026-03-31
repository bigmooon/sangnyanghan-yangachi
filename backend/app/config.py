from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # LLM Provider
    openai_api_key: str = ""
    llm_provider: str = "openai"
    main_model: str = "gpt-4o"
    embed_model: str = "text-embedding-3-small"

    # Ollama (SLM)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2:3b"

    # ChromaDB
    chromadb_host: str = "localhost"
    chromadb_port: int = 8001

    # Server
    backend_port: int = 8000
    cors_origins: list[str] = ["http://localhost:5173"]
    debug: bool = False
    app_name: str = "상냥한 양아치로 살아남기"
    use_langgraph: bool = True

    @model_validator(mode="after")
    def validate_api_keys(self) -> "Settings":
        if self.llm_provider == "openai" and not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY must be set when llm_provider is 'openai'")
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()
