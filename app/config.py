"""Application configuration.

Loads settings from the environment (and a local .env in development).
No secrets live in source control; see .env.example for the keys.
Implements build task T-0.3.
"""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Typed application settings, sourced from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service metadata
    app_name: str = "acme-operations-agent"
    app_version: str = "0.1.0"
    environment: str = Field(default="local")

    # PostgreSQL (durable structured data — see specs/data-spec.md)
    database_url: str = Field(default="postgresql://acme:acme@postgres:5432/acme")

    # Redis (per-session memory — see specs/data-spec.md section 3)
    redis_url: str = Field(default="redis://redis:6379/0")
    session_ttl_seconds: int = Field(default=3600)

    # Keycloak (OIDC auth + RBAC — see specs/adr/0004-keycloak-rbac.md)
    keycloak_url: str = Field(default="http://keycloak:8080")
    keycloak_realm: str = Field(default="acme")
    keycloak_client_id: str = Field(default="acme-agent")

    # Ollama (local LLM runtime — see specs/adr/0002-ollama-llm-runtime.md)
    ollama_url: str = Field(default="http://ollama:11434")
    # Pinned model + tag for reproducible evaluation (see specs/agent-spec.md section 6).
    ollama_model: str = Field(default="llama3.1:8b")

    # Arize Phoenix / OpenTelemetry (traces + eval — see specs/observability-spec.md)
    phoenix_collector_endpoint: str = Field(default="http://phoenix:6006")
    otel_service_name: str = Field(default="acme-operations-agent")


@lru_cache
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
