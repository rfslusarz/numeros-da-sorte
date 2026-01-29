"""
Modelos Pydantic para validação de request/response.
Define a estrutura de dados da API.
"""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class HealthResponse(BaseModel):
    """Resposta do endpoint de health check."""
    
    status: str = Field(..., description="Status da API")
    timestamp: str = Field(..., description="Timestamp da verificação")
    version: Optional[str] = Field(None, description="Versão da API")
    cache_type: Optional[str] = Field(None, description="Tipo de cache em uso")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "status": "ok",
                "timestamp": "2024-01-15T10:30:00",
                "version": "1.0.0",
                "cache_type": "redis"
            }
        }
    }


class EstimateResponse(BaseModel):
    """Resposta do endpoint de estimativa."""
    
    data: str = Field(..., description="Data da estimativa")
    quadra: List[int] = Field(..., description="4 números mais prováveis")
    quina: List[int] = Field(..., description="5 números mais prováveis")
    sorte: List[int] = Field(..., description="6 números mais prováveis (sena)")
    
    @field_validator('quadra')
    @classmethod
    def validate_quadra(cls, v: List[int]) -> List[int]:
        """Valida que quadra tem exatamente 4 números."""
        if len(v) != 4:
            raise ValueError('Quadra deve ter exatamente 4 números')
        if not all(1 <= num <= 60 for num in v):
            raise ValueError('Números devem estar entre 1 e 60')
        return v
    
    @field_validator('quina')
    @classmethod
    def validate_quina(cls, v: List[int]) -> List[int]:
        """Valida que quina tem exatamente 5 números."""
        if len(v) != 5:
            raise ValueError('Quina deve ter exatamente 5 números')
        if not all(1 <= num <= 60 for num in v):
            raise ValueError('Números devem estar entre 1 e 60')
        return v
    
    @field_validator('sorte')
    @classmethod
    def validate_sorte(cls, v: List[int]) -> List[int]:
        """Valida que sorte tem exatamente 6 números."""
        if len(v) != 6:
            raise ValueError('Sorte deve ter exatamente 6 números')
        if not all(1 <= num <= 60 for num in v):
            raise ValueError('Números devem estar entre 1 e 60')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "2024-01-15",
                "quadra": [5, 12, 23, 45],
                "quina": [5, 12, 23, 45, 58],
                "sorte": [5, 12, 23, 45, 58, 60]
            }
        }
    }


class DrawResponse(BaseModel):
    """Resposta do endpoint de busca de concurso por data."""
    
    data: str = Field(..., description="Data do concurso")
    numero_concurso: str = Field(..., description="Número do concurso")
    numeros: List[int] = Field(..., description="Números sorteados")
    
    @field_validator('numeros')
    @classmethod
    def validate_numeros(cls, v: List[int]) -> List[int]:
        """Valida que há 6 números sorteados."""
        if len(v) != 6:
            raise ValueError('Deve haver exatamente 6 números sorteados')
        if not all(1 <= num <= 60 for num in v):
            raise ValueError('Números devem estar entre 1 e 60')
        return v
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "data": "15/01/2024",
                "numero_concurso": "2650",
                "numeros": [5, 12, 23, 45, 58, 60]
            }
        }
    }


class ErrorResponse(BaseModel):
    """Resposta de erro padronizada."""
    
    detail: str = Field(..., description="Mensagem de erro")
    error_code: Optional[str] = Field(None, description="Código do erro")
    timestamp: Optional[str] = Field(None, description="Timestamp do erro")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Nenhum concurso encontrado para a data 2024-01-15",
                "error_code": "DRAW_NOT_FOUND",
                "timestamp": "2024-01-15T10:30:00"
            }
        }
    }


class DateParam(BaseModel):
    """Validação de parâmetro de data."""
    
    date: str = Field(..., description="Data no formato YYYY-MM-DD")
    
    @field_validator('date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Valida formato da data."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Data deve estar no formato YYYY-MM-DD')
        return v
    
    @field_validator('date')
    @classmethod
    def validate_date_range(cls, v: str) -> str:
        """Valida que a data não é futura."""
        date_obj = datetime.strptime(v, '%Y-%m-%d')
        if date_obj > datetime.now():
            raise ValueError('Data não pode ser futura')
        # Valida que não é muito antiga (últimos 5 anos)
        min_date = datetime.now().replace(year=datetime.now().year - 5)
        if date_obj < min_date:
            raise ValueError('Data deve ser dos últimos 5 anos')
        return v
