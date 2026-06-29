from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    embedding_provider: str = "cohere"
    cohere_api_key: str = ""
    source_dir: str = "./data/docs"
    chroma_path: str = "./data/chroma"
    metadata_registry_path: str = "./data/document_registry.json"
    collection_name: str = "intrabot"
    max_tokens: int = 512
    pdf_do_ocr: bool = False
    pdf_do_table_structure: bool = False
    pdf_page_batch_size: int = 50


settings = Settings()