from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    # Qdrant — local path mode by default (no Docker required)
    # Set QDRANT_PATH="" to switch to host/port server mode instead.
    qdrant_path: str = "./qdrant_data"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection: str = "govt_schemes"

    # Embeddings
    embedding_model: str = "BAAI/bge-small-en-v1.5"
    embedding_dim: int = 384

    # Generation
    google_api_key: str
    google_model: str = "gemini-3-flash-preview"

    # Ingestion
    chunk_size: int = 512
    chunk_overlap: int = 64


settings = Settings()
