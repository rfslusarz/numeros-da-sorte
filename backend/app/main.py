"""
Aplicação principal FastAPI.
Configuração e inicialização da API.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import api
import asyncio

app = FastAPI(
    title="API Mega-Sena - Estimativa Probabilística",
    description="API para estimativa de números mais prováveis da Mega-Sena",
    version="1.0.0"
)

# Configura CORS para permitir requisições do frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, especificar domínios permitidos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra as rotas
app.include_router(api.router, prefix="/api", tags=["api"])


@app.on_event("startup")
async def warmup_cache():
    try:
        await asyncio.to_thread(api.service.get_processed_data)
    except Exception:
        pass

@app.get("/")
async def root():
    """
    Endpoint raiz da API.
    
    Returns:
        Mensagem de boas-vindas
    """
    return {
        "message": "API Mega-Sena - Estimativa Probabilística",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "estimate": "/api/estimate",
            "draw": "/api/draw/{date}"
        }
    }
