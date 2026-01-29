"""
Circuit Breaker para proteger chamadas a serviços externos.
Implementa o padrão Circuit Breaker para evitar sobrecarga de serviços.
"""

from enum import Enum
from datetime import datetime, timedelta
from typing import Callable, Any
from functools import wraps
from app.utils.logger import get_logger
from app.exceptions import CircuitBreakerOpenError

logger = get_logger(__name__)


class CircuitState(Enum):
    """Estados do Circuit Breaker."""
    CLOSED = "closed"      # Funcionando normalmente
    OPEN = "open"          # Bloqueando requisições
    HALF_OPEN = "half_open"  # Testando recuperação


class CircuitBreaker:
    """
    Implementação do padrão Circuit Breaker.
    
    Estados:
    - CLOSED: Requisições passam normalmente
    - OPEN: Requisições são bloqueadas
    - HALF_OPEN: Permite algumas requisições para testar recuperação
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        expected_exception: type = Exception
    ):
        """
        Inicializa o Circuit Breaker.
        
        Args:
            failure_threshold: Número de falhas para abrir o circuito
            recovery_timeout: Tempo em segundos antes de tentar recuperar
            expected_exception: Tipo de exceção que conta como falha
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self._failure_count = 0
        self._last_failure_time: datetime = None
        self._state = CircuitState.CLOSED
        
        logger.info(
            f"Circuit breaker initialized: "
            f"threshold={failure_threshold}, timeout={recovery_timeout}s"
        )
    
    @property
    def state(self) -> CircuitState:
        """Retorna o estado atual do circuit breaker."""
        # Se está OPEN, verifica se deve mudar para HALF_OPEN
        if self._state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._state = CircuitState.HALF_OPEN
                logger.info("Circuit breaker changed to HALF_OPEN")
        
        return self._state
    
    def _should_attempt_reset(self) -> bool:
        """Verifica se deve tentar resetar o circuito."""
        if self._last_failure_time is None:
            return False
        
        elapsed = datetime.now() - self._last_failure_time
        return elapsed >= timedelta(seconds=self.recovery_timeout)
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executa uma função protegida pelo circuit breaker.
        
        Args:
            func: Função a executar
            *args: Argumentos posicionais
            **kwargs: Argumentos nomeados
        
        Returns:
            Resultado da função
        
        Raises:
            CircuitBreakerOpenError: Se o circuito estiver aberto
        """
        if self.state == CircuitState.OPEN:
            logger.warning("Circuit breaker is OPEN, blocking request")
            raise CircuitBreakerOpenError()
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _on_success(self):
        """Chamado quando uma requisição é bem-sucedida."""
        if self._state == CircuitState.HALF_OPEN:
            logger.info("Circuit breaker recovered, changing to CLOSED")
            self._state = CircuitState.CLOSED
        
        self._failure_count = 0
        self._last_failure_time = None
    
    def _on_failure(self):
        """Chamado quando uma requisição falha."""
        self._failure_count += 1
        self._last_failure_time = datetime.now()
        
        logger.warning(
            f"Circuit breaker failure: {self._failure_count}/{self.failure_threshold}"
        )
        
        if self._failure_count >= self.failure_threshold:
            self._state = CircuitState.OPEN
            logger.error(
                f"Circuit breaker OPENED after {self._failure_count} failures"
            )
    
    def reset(self):
        """Reseta manualmente o circuit breaker."""
        self._failure_count = 0
        self._last_failure_time = None
        self._state = CircuitState.CLOSED
        logger.info("Circuit breaker manually reset")
    
    def get_stats(self) -> dict:
        """Retorna estatísticas do circuit breaker."""
        return {
            "state": self.state.value,
            "failure_count": self._failure_count,
            "failure_threshold": self.failure_threshold,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None
        }


def circuit_breaker(
    failure_threshold: int = 5,
    recovery_timeout: int = 30,
    expected_exception: type = Exception
):
    """
    Decorator para aplicar circuit breaker a uma função.
    
    Args:
        failure_threshold: Número de falhas para abrir o circuito
        recovery_timeout: Tempo em segundos antes de tentar recuperar
        expected_exception: Tipo de exceção que conta como falha
    
    Example:
        @circuit_breaker(failure_threshold=3, recovery_timeout=60)
        def call_external_api():
            # código que pode falhar
            pass
    """
    cb = CircuitBreaker(failure_threshold, recovery_timeout, expected_exception)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            return cb.call(func, *args, **kwargs)
        
        # Adiciona métodos do circuit breaker à função
        wrapper.circuit_breaker = cb
        wrapper.reset = cb.reset
        wrapper.get_stats = cb.get_stats
        
        return wrapper
    
    return decorator


# Instância global de circuit breaker para API externa
_api_circuit_breaker: CircuitBreaker = None


def get_api_circuit_breaker() -> CircuitBreaker:
    """Obtém a instância global do circuit breaker para API externa."""
    global _api_circuit_breaker
    
    if _api_circuit_breaker is None:
        from app.config import settings
        _api_circuit_breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_failure_threshold,
            recovery_timeout=settings.circuit_breaker_recovery_timeout,
            expected_exception=Exception
        )
    
    return _api_circuit_breaker
