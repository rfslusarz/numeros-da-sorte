"""
Sistema de logging estruturado para a aplicação.
Suporta formato JSON e texto com níveis configuráveis.
"""

import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """Formatter para logs em formato JSON."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Formata o log record como JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Adiciona informações de exceção se houver
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Adiciona campos extras se houver
        if hasattr(record, "extra_fields"):
            log_data.update(record.extra_fields)
        
        return json.dumps(log_data, ensure_ascii=False)


class TextFormatter(logging.Formatter):
    """Formatter para logs em formato texto legível."""
    
    def __init__(self):
        fmt = (
            "%(asctime)s - %(name)s - %(levelname)s - "
            "%(module)s:%(funcName)s:%(lineno)d - %(message)s"
        )
        super().__init__(fmt=fmt, datefmt="%Y-%m-%d %H:%M:%S")


def setup_logger(
    name: str,
    level: str = "INFO",
    log_format: str = "json",
    log_file: str = None
) -> logging.Logger:
    """
    Configura e retorna um logger.
    
    Args:
        name: Nome do logger
        level: Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Formato do log ('json' ou 'text')
        log_file: Caminho do arquivo de log (opcional)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Remove handlers existentes
    logger.handlers.clear()
    
    # Seleciona o formatter
    if log_format.lower() == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    # Handler para console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler para arquivo se especificado
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    # Previne propagação para o root logger
    logger.propagate = False
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """
    Obtém um logger existente ou cria um novo.
    
    Args:
        name: Nome do logger (usa __name__ se None)
    
    Returns:
        Logger
    """
    if name is None:
        name = __name__
    
    logger = logging.getLogger(name)
    
    # Se o logger não tem handlers, configura com defaults
    if not logger.handlers:
        from app.config import settings
        return setup_logger(
            name=name,
            level=settings.log_level,
            log_format=settings.log_format
        )
    
    return logger


class LoggerAdapter(logging.LoggerAdapter):
    """Adapter para adicionar campos extras aos logs."""
    
    def process(self, msg: str, kwargs: Dict[str, Any]) -> tuple:
        """Processa a mensagem adicionando campos extras."""
        extra = kwargs.get("extra", {})
        
        # Adiciona campos extras ao record
        if "extra_fields" not in kwargs:
            kwargs["extra_fields"] = {}
        
        kwargs["extra_fields"].update(extra)
        
        return msg, kwargs


def log_request(logger: logging.Logger, method: str, path: str, status_code: int, duration: float):
    """
    Loga uma requisição HTTP.
    
    Args:
        logger: Logger a usar
        method: Método HTTP
        path: Caminho da requisição
        status_code: Código de status da resposta
        duration: Duração da requisição em segundos
    """
    logger.info(
        f"{method} {path} - {status_code}",
        extra={
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": round(duration * 1000, 2)
        }
    )


def log_error(logger: logging.Logger, error: Exception, context: Dict[str, Any] = None):
    """
    Loga um erro com contexto adicional.
    
    Args:
        logger: Logger a usar
        error: Exceção ocorrida
        context: Contexto adicional (opcional)
    """
    extra = {
        "error_type": type(error).__name__,
        "error_message": str(error)
    }
    
    if context:
        extra.update(context)
    
    logger.error(
        f"Error: {str(error)}",
        exc_info=True,
        extra=extra
    )
