"""
Rotas da API REST.
Define os endpoints disponíveis com validação e tratamento de erros.
Versão refatorada com modelos Pydantic e logging estruturado.
"""

from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from app.services.mega_sena_service import MegaSenaService
from app.models import (
    HealthResponse,
    EstimateResponse,
    DrawResponse,
    ErrorResponse
)
from app.exceptions import (
    APIConnectionError,
    DataProcessingError,
    DrawNotFoundError,
    CircuitBreakerOpenError
)
from app.utils.logger import get_logger
from app.config import settings

logger = get_logger(__name__)
router = APIRouter()
service = MegaSenaService()


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check",
    description="Verifica o status de saúde da API e retorna informações do sistema"
)
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Status da API com informações do sistema
    """
    logger.info("Health check requested")
    
    stats = service.get_stats()
    
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        version=settings.api_version,
        cache_type=stats.get("cache_type")
    )


@router.get(
    "/estimate",
    response_model=EstimateResponse,
    responses={
        500: {"model": ErrorResponse, "description": "Erro ao gerar estimativa"},
        503: {"model": ErrorResponse, "description": "Serviço temporariamente indisponível"}
    },
    summary="Gerar Estimativa",
    description="Retorna estimativa de números mais prováveis baseada em análise histórica"
)
async def get_estimate():
    """
    Retorna estimativa de números mais prováveis.
    
    Analisa os concursos dos últimos 2 anos e retorna os números
    mais frequentes organizados em quadra, quina e sena.
    
    Returns:
        Estimativa com quadra, quina e sorte (sena)
    
    Raises:
        HTTPException: Em caso de erro ao gerar estimativa
    """
    logger.info("Estimate requested")
    
    try:
        estimate = service.get_estimate()
        
        return EstimateResponse(
            data=estimate["data"],
            quadra=estimate["quadra"],
            quina=estimate["quina"],
            sorte=estimate["sorte"]
        )
    
    except CircuitBreakerOpenError as e:
        logger.error(f"Circuit breaker open: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "detail": "Serviço temporariamente indisponível. Tente novamente em alguns instantes.",
                "error_code": e.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except APIConnectionError as e:
        logger.error(f"API connection error: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "detail": str(e),
                "error_code": e.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except DataProcessingError as e:
        logger.error(f"Data processing error: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": str(e),
                "error_code": e.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error generating estimate: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "detail": f"Erro inesperado ao gerar estimativa: {str(e)}",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get(
    "/draw/{date}",
    response_model=DrawResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Data inválida"},
        404: {"model": ErrorResponse, "description": "Concurso não encontrado"},
        500: {"model": ErrorResponse, "description": "Erro ao buscar concurso"}
    },
    summary="Buscar Concurso por Data",
    description="Retorna os números sorteados em uma data específica"
)
async def get_draw_by_date(date: str):
    """
    Retorna os números sorteados em uma data específica.
    
    Args:
        date: Data no formato YYYY-MM-DD
    
    Returns:
        Dados do concurso incluindo números sorteados
    
    Raises:
        HTTPException: Em caso de data inválida ou concurso não encontrado
    """
    logger.info(f"Draw requested for date: {date}")
    
    try:
        # Valida formato da data
        datetime.strptime(date, '%Y-%m-%d')
        
        # Busca concurso
        draw_data = service.get_draw_by_date(date)
        
        return DrawResponse(
            data=draw_data["data"],
            numero_concurso=draw_data["numero_concurso"],
            numeros=draw_data["numeros"]
        )
    
    except ValueError:
        logger.warning(f"Invalid date format: {date}")
        raise HTTPException(
            status_code=400,
            detail={
                "detail": "Formato de data inválido. Use YYYY-MM-DD",
                "error_code": "INVALID_DATE",
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except DrawNotFoundError as e:
        logger.info(f"Draw not found for date: {date}")
        raise HTTPException(
            status_code=404,
            detail={
                "detail": str(e),
                "error_code": e.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except CircuitBreakerOpenError as e:
        logger.error(f"Circuit breaker open: {e}")
        raise HTTPException(
            status_code=503,
            detail={
                "detail": "Serviço temporariamente indisponível. Tente novamente em alguns instantes.",
                "error_code": e.error_code,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    except Exception as e:
        logger.error(f"Unexpected error fetching draw: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail={
                "detail": f"Erro ao buscar concurso: {str(e)}",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.post(
    "/cache/clear",
    summary="Limpar Cache",
    description="Limpa todo o cache do sistema (requer permissões administrativas)"
)
async def clear_cache():
    """
    Limpa todo o cache do sistema.
    
    Returns:
        Mensagem de confirmação
    """
    logger.info("Cache clear requested")
    
    try:
        service.clear_cache()
        return {
            "message": "Cache limpo com sucesso",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": f"Erro ao limpar cache: {str(e)}",
                "error_code": "CACHE_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        )


@router.get(
    "/stats",
    summary="Estatísticas do Sistema",
    description="Retorna estatísticas e métricas do sistema"
)
async def get_stats():
    """
    Retorna estatísticas do sistema.
    
    Returns:
        Estatísticas incluindo cache e circuit breaker
    """
    logger.info("Stats requested")
    
    try:
        stats = service.get_stats()
        return {
            "cache_type": stats.get("cache_type"),
            "circuit_breaker": stats.get("circuit_breaker"),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(
            status_code=500,
            detail={
                "detail": f"Erro ao obter estatísticas: {str(e)}",
                "error_code": "INTERNAL_ERROR",
                "timestamp": datetime.now().isoformat()
            }
        )
