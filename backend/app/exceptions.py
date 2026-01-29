"""
Exceções customizadas para a aplicação.
Permite tratamento de erros mais específico e informativo.
"""


class MegaSenaException(Exception):
    """Exceção base para erros da aplicação."""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code or "INTERNAL_ERROR"
        super().__init__(self.message)


class APIConnectionError(MegaSenaException):
    """Erro ao conectar com a API externa da Mega-Sena."""
    
    def __init__(self, message: str = "Erro ao conectar com a API da Mega-Sena"):
        super().__init__(message, error_code="API_CONNECTION_ERROR")


class DataProcessingError(MegaSenaException):
    """Erro ao processar dados dos concursos."""
    
    def __init__(self, message: str = "Erro ao processar dados"):
        super().__init__(message, error_code="DATA_PROCESSING_ERROR")


class DrawNotFoundError(MegaSenaException):
    """Concurso não encontrado para a data especificada."""
    
    def __init__(self, date: str):
        message = f"Nenhum concurso encontrado para a data {date}"
        super().__init__(message, error_code="DRAW_NOT_FOUND")
        self.date = date


class InvalidDateError(MegaSenaException):
    """Data fornecida é inválida."""
    
    def __init__(self, message: str = "Data inválida"):
        super().__init__(message, error_code="INVALID_DATE")


class CacheError(MegaSenaException):
    """Erro relacionado ao sistema de cache."""
    
    def __init__(self, message: str = "Erro no sistema de cache"):
        super().__init__(message, error_code="CACHE_ERROR")


class CircuitBreakerOpenError(MegaSenaException):
    """Circuit breaker está aberto, requisições bloqueadas."""
    
    def __init__(self, message: str = "Serviço temporariamente indisponível"):
        super().__init__(message, error_code="CIRCUIT_BREAKER_OPEN")


class RateLimitExceededError(MegaSenaException):
    """Limite de requisições excedido."""
    
    def __init__(self, message: str = "Limite de requisições excedido"):
        super().__init__(message, error_code="RATE_LIMIT_EXCEEDED")
