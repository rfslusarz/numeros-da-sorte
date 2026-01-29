"""
Aplicação principal FastAPI.
Configuração e inicialização da API com middleware e tratamento de erros.
Versão refatorada com rate limiting, logging e segurança.
"""

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import time
from datetime import datetime

from app.routes import api
from app.config import settings
from app.utils.logger import get_logger, log_request
from app.exceptions import MegaSenaException

# Configuração de logging
logger = get_logger(__name__)

# Configuração de rate limiting
limiter = Limiter(key_func=get_remote_address)

# Criação da aplicação
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Adiciona rate limiting à aplicação
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Middleware de logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware para logar todas as requisições."""
    start_time = time.time()
    
    # Log da requisição
    logger.info(
        f"Request started: {request.method} {request.url.path}",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client": request.client.host if request.client else "unknown"
        }
    )
    
    # Processa requisição
    response = await call_next(request)
    
    # Calcula duração
    duration = time.time() - start_time
    
    # Log da resposta
    log_request(
        logger,
        request.method,
        request.url.path,
        response.status_code,
        duration
    )
    
    # Adiciona headers customizados
    response.headers["X-Process-Time"] = str(duration)
    response.headers["X-API-Version"] = settings.api_version
    
    return response


# Middleware de segurança
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    """Adiciona headers de segurança às respostas."""
    response = await call_next(request)
    
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    
    return response


# Configura CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers globais
@app.exception_handler(MegaSenaException)
async def mega_sena_exception_handler(request: Request, exc: MegaSenaException):
    """Handler para exceções customizadas da aplicação."""
    logger.error(
        f"MegaSena exception: {exc.message}",
        extra={
            "error_code": exc.error_code,
            "path": request.url.path
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": exc.message,
            "error_code": exc.error_code,
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler para erros de validação do Pydantic."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": exc.errors(),
            "error_code": "VALIDATION_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler para exceções não tratadas."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path}
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Erro interno do servidor",
            "error_code": "INTERNAL_ERROR",
            "timestamp": datetime.now().isoformat()
        }
    )


# Eventos de ciclo de vida
@app.on_event("startup")
async def startup_event():
    """Executado ao iniciar a aplicação."""
    logger.info(
        f"Starting {settings.api_title} v{settings.api_version}",
        extra={
            "cache_type": settings.cache_type,
            "rate_limit_enabled": settings.rate_limit_enabled
        }
    )
    
    # Aquecimento do cache em background
    try:
        import asyncio
        asyncio.create_task(warmup_cache())
    except Exception as e:
        logger.warning(f"Cache warmup failed: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """Executado ao desligar a aplicação."""
    logger.info("Shutting down application")


async def warmup_cache():
    """Aquece o cache com dados iniciais."""
    try:
        logger.info("Starting cache warmup")
        import asyncio
        await asyncio.to_thread(api.service.get_processed_data)
        logger.info("Cache warmup completed")
    except Exception as e:
        logger.error(f"Cache warmup error: {e}")


# Registra as rotas
app.include_router(api.router, prefix="/api", tags=["api"])


# Endpoint raiz
@app.get("/", tags=["root"])
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def root(request: Request):
    """
    Endpoint raiz da API.
    
    Returns:
        Informações básicas da API
    """
    return {
        "message": settings.api_title,
        "version": settings.api_version,
        "docs": "/docs",
        "endpoints": {
            "health": "/api/health",
            "estimate": "/api/estimate",
            "draw": "/api/draw/{date}",
            "stats": "/api/stats",
            "cache_clear": "/api/cache/clear"
        },
        "timestamp": datetime.now().isoformat()
    }


# Endpoint de health check adicional
@app.get("/health", tags=["health"])
async def health():
    """Health check simplificado."""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
