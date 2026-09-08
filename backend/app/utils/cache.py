"""
HealthConnect AI - Cache Manager
=================================
Redis cache management with fallback to in-memory.

Features:
- Redis connection pool
- In-memory fallback
- TTL management
- Cache decorators
- Batch operations
"""

import json
import time
from typing import Optional, Any, Dict, List, Callable
from functools import wraps
import hashlib

import redis.asyncio as redis
from redis.asyncio import Redis

from config.settings import get_settings
from config.logging_config import get_logger
from config.constants import CACHE_TTL, CACHE_PREFIX

logger = get_logger(__name__)
settings = get_settings()


class CacheManager:
    """
    Redis cache manager with in-memory fallback.
    Singleton pattern for connection reuse.
    """
    
    _instance = None
    _redis_client: Optional[Redis] = None
    _memory_cache: Dict[str, Dict[str, Any]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def initialize(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self._redis_client = redis.from_url(
                settings.redis.URL,
                password=settings.redis.PASSWORD or None,
                db=settings.redis.DB,
                max_connections=settings.redis.MAX_CONNECTIONS,
                socket_timeout=settings.redis.SOCKET_TIMEOUT,
                socket_connect_timeout=settings.redis.SOCKET_CONNECT_TIMEOUT,
                decode_responses=True,
            )
            
            # Test connection
            await self._redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.warning(f"Redis connection failed: {e}. Using in-memory cache.")
            self._redis_client = None
    
    async def close(self) -> None:
        """Close Redis connection"""
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None
    
    async def get(self, key: str, default: Any = None) -> Any:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Any: Cached value or default
        """
        if self._redis_client:
            try:
                value = await self._redis_client.get(key)
                if value:
                    return json.loads(value)
                return default
            except Exception as e:
                logger.error(f"Redis get failed: {e}")
        
        # In-memory fallback
        cache_entry = self._memory_cache.get(key)
        if cache_entry and cache_entry["expires_at"] > time.time():
            return cache_entry["value"]
        
        if cache_entry:
            del self._memory_cache[key]
        
        return default
    
    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
            
        Returns:
            bool: True if successful
        """
        if self._redis_client:
            try:
                serialized = json.dumps(value)
                await self._redis_client.set(key, serialized, ex=ttl)
                return True
            except Exception as e:
                logger.error(f"Redis set failed: {e}")
        
        # In-memory fallback
        self._memory_cache[key] = {
            "value": value,
            "expires_at": time.time() + (ttl or 3600),
        }
        return True
    
    async def delete(self, key: str) -> bool:
        """
        Delete value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if deleted
        """
        if self._redis_client:
            try:
                await self._redis_client.delete(key)
                return True
            except Exception as e:
                logger.error(f"Redis delete failed: {e}")
        
        if key in self._memory_cache:
            del self._memory_cache[key]
            return True
        
        return False
    
    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.
        
        Args:
            key: Cache key
            
        Returns:
            bool: True if exists
        """
        if self._redis_client:
            try:
                return await self._redis_client.exists(key) > 0
            except Exception as e:
                logger.error(f"Redis exists failed: {e}")
        
        cache_entry = self._memory_cache.get(key)
        if cache_entry and cache_entry["expires_at"] > time.time():
            return True
        
        return False
    
    async def get_or_set(
        self,
        key: str,
        callback: Callable,
        ttl: Optional[int] = None,
    ) -> Any:
        """
        Get value from cache or compute and store.
        
        Args:
            key: Cache key
            callback: Function to compute value if not cached
            ttl: Time-to-live
            
        Returns:
            Any: Cached or computed value
        """
        # Try cache first
        value = await self.get(key)
        if value is not None:
            return value
        
        # Compute value
        value = await callback() if hasattr(callback, '__await__') else callback()
        
        # Store in cache
        if value is not None:
            await self.set(key, value, ttl)
        
        return value
    
    async def clear_prefix(self, prefix: str) -> int:
        """
        Clear all keys with prefix.
        
        Args:
            prefix: Key prefix
            
        Returns:
            int: Number of keys deleted
        """
        if self._redis_client:
            try:
                keys = await self._redis_client.keys(f"{prefix}*")
                if keys:
                    return await self._redis_client.delete(*keys)
                return 0
            except Exception as e:
                logger.error(f"Redis clear_prefix failed: {e}")
        
        # In-memory fallback
        keys_to_delete = [k for k in self._memory_cache if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._memory_cache[key]
        
        return len(keys_to_delete)
    
    async def increment(self, key: str, amount: int = 1, ttl: Optional[int] = None) -> int:
        """
        Increment counter in cache.
        
        Args:
            key: Cache key
            amount: Increment amount
            ttl: TTL for counter
            
        Returns:
            int: New counter value
        """
        if self._redis_client:
            try:
                value = await self._redis_client.incrby(key, amount)
                if ttl:
                    await self._redis_client.expire(key, ttl)
                return value
            except Exception as e:
                logger.error(f"Redis increment failed: {e}")
        
        # In-memory fallback
        current = self._memory_cache.get(key, {}).get("value", 0)
        new_value = current + amount
        self._memory_cache[key] = {
            "value": new_value,
            "expires_at": time.time() + (ttl or 3600),
        }
        return new_value
    
    async def decrement(self, key: str, amount: int = 1) -> int:
        """
        Decrement counter in cache.
        
        Args:
            key: Cache key
            amount: Decrement amount
            
        Returns:
            int: New counter value
        """
        return await self.increment(key, -amount)
    
    async def get_many(self, keys: List[str]) -> Dict[str, Any]:
        """
        Get multiple values from cache.
        
        Args:
            keys: List of cache keys
            
        Returns:
            Dict: Key-value pairs
        """
        result = {}
        
        for key in keys:
            value = await self.get(key)
            if value is not None:
                result[key] = value
        
        return result
    
    async def set_many(
        self,
        data: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> bool:
        """
        Set multiple values in cache.
        
        Args:
            data: Key-value pairs
            ttl: TTL for all values
            
        Returns:
            bool: True if all set successfully
        """
        for key, value in data.items():
            await self.set(key, value, ttl)
        
        return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict: Cache statistics
        """
        if self._redis_client:
            try:
                info = await self._redis_client.info()
                return {
                    "type": "redis",
                    "used_memory": info.get("used_memory", 0),
                    "connected_clients": info.get("connected_clients", 0),
                    "total_keys": await self._redis_client.dbsize(),
                    "hits": info.get("keyspace_hits", 0),
                    "misses": info.get("keyspace_misses", 0),
                }
            except Exception as e:
                logger.error(f"Redis stats failed: {e}")
        
        return {
            "type": "memory",
            "total_keys": len(self._memory_cache),
            "hits": 0,
            "misses": 0,
        }


def cache_key(prefix: str, *args, **kwargs) -> str:
    """
    Generate cache key from arguments.
    
    Args:
        prefix: Key prefix
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        str: Generated cache key
    """
    key_parts = [prefix]
    
    for arg in args:
        key_parts.append(str(arg))
    
    for k, v in sorted(kwargs.items()):
        key_parts.append(f"{k}:{v}")
    
    key = ":".join(key_parts)
    
    if len(key) > 200:
        key = f"{prefix}:{hashlib.sha256(key.encode()).hexdigest()[:32]}"
    
    return key


def cached(ttl: Optional[int] = None, prefix: str = "cache"):
    """
    Cache decorator for async functions.
    
    Args:
        ttl: Time-to-live in seconds
        prefix: Cache key prefix
        
    Returns:
        Decorator function
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_manager = CacheManager()
            key = cache_key(prefix, func.__name__, *args, **kwargs)
            
            return await cache_manager.get_or_set(
                key,
                lambda: func(*args, **kwargs),
                ttl,
            )
        
        return wrapper
    
    return decorator


async def check_redis_connection() -> bool:
    """Check if Redis is available"""
    cache_manager = CacheManager()
    await cache_manager.initialize()
    return cache_manager._redis_client is not None