"""
Configuração centralizada da aplicação usando Pydantic Settings.
Carrega variáveis de ambiente do arquivo .env
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Configurações da aplicação."""
    
    # API Configuration
    api_title: str = Field(
        default="API Mega-Sena - Estimativa Probabilística",
        description="Título da API"
    )
    api_version: str = Field(default="1.0.0", description="Versão da API")
    api_description: str = Field(
        default="API para estimativa de números mais prováveis da Mega-Sena",
        description="Descrição da API"
    )
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", description="Host do servidor")
    port: int = Field(default=8000, description="Porta do servidor")
    debug: bool = Field(default=False, description="Modo debug")
    reload: bool = Field(default=False, description="Auto-reload")
    
    # CORS Configuration
    cors_origins: List[str] = Field(
        default=["http://localhost:8080", "http://localhost:3000"],
        description="Origens permitidas para CORS"
    )
    
    # External API
    mega_sena_api_url: str = Field(
        default="https://servicebus2.caixa.gov.br/portaldeloterias/api/megasena",
        description="URL da API da Mega-Sena"
    )
    
    # Cache Configuration
    cache_type: str = Field(
        default="memory",
        description="Tipo de cache: 'memory' ou 'redis'"
    )
    cache_ttl: int = Field(
        default=3600,
        description="TTL do cache em segundos"
    )
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="URL do Redis"
    )
    
    # Rate Limiting
    rate_limit_enabled: bool = Field(
        default=True,
        description="Habilitar rate limiting"
    )
    rate_limit_per_minute: int = Field(
        default=60,
        description="Requisições permitidas por minuto"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Nível de log")
    log_format: str = Field(
        default="json",
        description="Formato de log: 'json' ou 'text'"
    )
    
    # Circuit Breaker
    circuit_breaker_failure_threshold: int = Field(
        default=5,
        description="Número de falhas para abrir o circuit breaker"
    )
    circuit_breaker_timeout: int = Field(
        default=60,
        description="Timeout em segundos para requisições"
    )
    circuit_breaker_recovery_timeout: int = Field(
        default=30,
        description="Tempo em segundos antes de tentar recuperar"
    )
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )


# Instância global de configurações
settings = Settings()
