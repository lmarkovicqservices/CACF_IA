from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    """Configuración de la aplicación cargada desde variables de entorno."""

    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-small"

    # WhatsApp
    whatsapp_verify_token: str
    whatsapp_access_token: str
    whatsapp_phone_number_id: str
    whatsapp_business_account_id: str = ""
    whatsapp_app_secret: str

    # API Precios CACF
    cacf_precios_api_url: str
    cacf_precios_api_key: str = ""

    # API Validación Socios
    cacf_socios_api_url: str
    cacf_socios_api_key: str = ""

    # ChromaDB
    chroma_persist_dir: str = "./chroma_data"
    chroma_collection_name: str = "cacf_ensilado"

    # App
    app_env: str = "development"
    app_port: int = 8000
    log_level: str = "info"
    rate_limit_per_user: int = 20

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
