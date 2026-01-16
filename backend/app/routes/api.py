"""
Rotas da API REST.
Define os endpoints disponíveis.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
from app.services.mega_sena_service import MegaSenaService

router = APIRouter()
service = MegaSenaService()


@router.get("/health")
async def health_check():
    """
    Endpoint de verificação de saúde da API.
    
    Returns:
        Status da API
    """
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }


@router.get("/estimate")
async def get_estimate():
    """
    Retorna estimativa de números mais prováveis.
    
    Returns:
        Dicionário com data, quadra, quina e sorte
    """
    try:
        estimate = service.get_estimate()
        return {"data": estimate["data"], **estimate}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao gerar estimativa: {str(e)}")


@router.get("/draw/{date}")
async def get_draw_by_date(date: str):
    """
    Retorna os números sorteados em uma data específica.
    
    Args:
        date: Data no formato YYYY-MM-DD
        
    Returns:
        Dicionário com dados do concurso
    """
    try:
        # Valida formato da data
        datetime.strptime(date, '%Y-%m-%d')
        
        draw_data = service.get_draw_by_date(date)
        
        if draw_data is None:
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum concurso encontrado para a data {date}"
            )
        
        return draw_data
        
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Formato de data inválido. Use YYYY-MM-DD"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar concurso: {str(e)}"
        )
