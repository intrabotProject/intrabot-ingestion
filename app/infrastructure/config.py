from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    embedding_provider: str = "cohere"
    cohere_api_key: str = ""
    source_dir: str = "./data/docs"
    chroma_path: str = "./data/chroma"
    collection_name: str = "intrabot"
    max_tokens: int = 512


settings = Settings()