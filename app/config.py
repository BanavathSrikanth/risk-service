from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    service_name: str = "infraiq-risk-service"
    environment: str = "development"
    api_prefix: str = "/api/v1"
    tenant_id: str = "local"
    rules_directory: str = str(Path(__file__).parent / "domain" / "rules" / "v1")
    redis_url: str | None = None
    database_url: str = "sqlite:///risk-service.db"
    blob_connection_string: str | None = None
    blob_container: str = "infraiq"
    foundry_endpoint: str | None = None
    foundry_api_key: str | None = None
    osm_tile_url: str = "https://tile.openstreetmap.org/{z}/{x}/{y}.png"
    map_style_url: str = "https://demotiles.maplibre.org/style.json"
    osm_user_agent: str = "infraiq-risk-service/1.0"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
