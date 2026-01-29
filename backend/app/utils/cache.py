"""
Sistema de cache com suporte a Redis e fallback para memória.
Implementa interface comum para diferentes backends de cache.
"""

from abc import ABC, abstractmethod
from typing import Any, Optional
from datetime import datetime, timedelta
import json
import pickle
from app.utils.logger import get_logger
from app.exceptions import CacheError

logger = get_logger(__name__)


class CacheBackend(ABC):
    """Interface abstrata para backends de cache."""
    
    @abstractmethod
    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache."""
        pass
    
    @abstractmethod
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define um valor no cache com TTL."""
        pass
    
    @abstractmethod
    def delete(self, key: str) -> bool:
        """Remove um valor do cache."""
        pass
    
    @abstractmethod
    def clear(self) -> bool:
        """Limpa todo o cache."""
        pass
    
    @abstractmethod
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        pass


class MemoryCache(CacheBackend):
    """Implementação de cache em memória."""
    
    def __init__(self):
        self._cache: dict = {}
        self._expiry: dict = {}
        logger.info("Memory cache initialized")
    
    def _is_expired(self, key: str) -> bool:
        """Verifica se uma chave expirou."""
        if key not in self._expiry:
            return False
        return datetime.now() > self._expiry[key]
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache."""
        try:
            if key not in self._cache:
                logger.debug(f"Cache miss: {key}")
                return None
            
            if self._is_expired(key):
                logger.debug(f"Cache expired: {key}")
                self.delete(key)
                return None
            
            logger.debug(f"Cache hit: {key}")
            return self._cache[key]
        except Exception as e:
            logger.error(f"Error getting from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define um valor no cache com TTL."""
        try:
            self._cache[key] = value
            self._expiry[key] = datetime.now() + timedelta(seconds=ttl)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove um valor do cache."""
        try:
            if key in self._cache:
                del self._cache[key]
            if key in self._expiry:
                del self._expiry[key]
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from cache: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache."""
        try:
            self._cache.clear()
            self._expiry.clear()
            logger.info("Cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        return key in self._cache and not self._is_expired(key)


class RedisCache(CacheBackend):
    """Implementação de cache usando Redis."""
    
    def __init__(self, redis_url: str):
        try:
            import redis
            self._redis = redis.from_url(redis_url, decode_responses=False)
            # Testa conexão
            self._redis.ping()
            logger.info(f"Redis cache initialized: {redis_url}")
        except ImportError:
            raise CacheError("Redis package not installed. Install with: pip install redis")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise CacheError(f"Failed to connect to Redis: {e}")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache."""
        try:
            value = self._redis.get(key)
            if value is None:
                logger.debug(f"Cache miss: {key}")
                return None
            
            logger.debug(f"Cache hit: {key}")
            return pickle.loads(value)
        except Exception as e:
            logger.error(f"Error getting from Redis: {e}")
            return None
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define um valor no cache com TTL."""
        try:
            serialized = pickle.dumps(value)
            self._redis.setex(key, ttl, serialized)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Error setting Redis cache: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """Remove um valor do cache."""
        try:
            self._redis.delete(key)
            logger.debug(f"Cache deleted: {key}")
            return True
        except Exception as e:
            logger.error(f"Error deleting from Redis: {e}")
            return False
    
    def clear(self) -> bool:
        """Limpa todo o cache."""
        try:
            self._redis.flushdb()
            logger.info("Redis cache cleared")
            return True
        except Exception as e:
            logger.error(f"Error clearing Redis cache: {e}")
            return False
    
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        try:
            return bool(self._redis.exists(key))
        except Exception as e:
            logger.error(f"Error checking Redis key existence: {e}")
            return False


class CacheManager:
    """Gerenciador de cache com fallback automático."""
    
    def __init__(self, cache_type: str = "memory", redis_url: str = None):
        """
        Inicializa o gerenciador de cache.
        
        Args:
            cache_type: Tipo de cache ('memory' ou 'redis')
            redis_url: URL do Redis (necessário se cache_type='redis')
        """
        self.cache_type = cache_type
        
        if cache_type == "redis" and redis_url:
            try:
                self._backend = RedisCache(redis_url)
                logger.info("Using Redis cache")
            except CacheError as e:
                logger.warning(f"Redis unavailable, falling back to memory cache: {e}")
                self._backend = MemoryCache()
                self.cache_type = "memory"
        else:
            self._backend = MemoryCache()
            logger.info("Using memory cache")
    
    def get(self, key: str) -> Optional[Any]:
        """Obtém um valor do cache."""
        return self._backend.get(key)
    
    def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Define um valor no cache com TTL."""
        return self._backend.set(key, value, ttl)
    
    def delete(self, key: str) -> bool:
        """Remove um valor do cache."""
        return self._backend.delete(key)
    
    def clear(self) -> bool:
        """Limpa todo o cache."""
        return self._backend.clear()
    
    def exists(self, key: str) -> bool:
        """Verifica se uma chave existe no cache."""
        return self._backend.exists(key)
    
    def get_type(self) -> str:
        """Retorna o tipo de cache em uso."""
        return self.cache_type


# Instância global de cache
_cache_manager: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Obtém a instância global do cache manager."""
    global _cache_manager
    
    if _cache_manager is None:
        from app.config import settings
        _cache_manager = CacheManager(
            cache_type=settings.cache_type,
            redis_url=settings.redis_url
        )
    
    return _cache_manager
