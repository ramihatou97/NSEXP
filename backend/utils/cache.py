"""
Simple in-memory caching utility for single-user deployment
Uses Python's functools and dict for fast, lightweight caching
"""
from functools import wraps, lru_cache
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
import hashlib
import json
from utils.logger import get_logger

logger = get_logger(__name__)


class SimpleCache:
    """
    Simple in-memory cache for single-user deployment
    Thread-safe, TTL support, memory-efficient
    """

    def __init__(self, default_ttl: int = 300):
        """
        Initialize cache

        Args:
            default_ttl: Default time-to-live in seconds (default: 5 minutes)
        """
        self._cache = {}
        self._timestamps = {}
        self._default_ttl = default_ttl

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        if key not in self._cache:
            return None

        # Check if expired
        if self._is_expired(key):
            self.delete(key)
            return None

        logger.debug(f"Cache hit: {key}")
        return self._cache[key]

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        self._cache[key] = value
        self._timestamps[key] = {
            "created": datetime.utcnow(),
            "ttl": ttl or self._default_ttl
        }
        logger.debug(f"Cache set: {key} (TTL: {ttl or self._default_ttl}s)")

    def delete(self, key: str) -> None:
        """Delete key from cache"""
        self._cache.pop(key, None)
        self._timestamps.pop(key, None)
        logger.debug(f"Cache deleted: {key}")

    def clear(self) -> None:
        """Clear entire cache"""
        self._cache.clear()
        self._timestamps.clear()
        logger.info("Cache cleared")

    def _is_expired(self, key: str) -> bool:
        """Check if cache entry is expired"""
        if key not in self._timestamps:
            return True

        timestamp_info = self._timestamps[key]
        age = (datetime.utcnow() - timestamp_info["created"]).total_seconds()
        return age > timestamp_info["ttl"]

    def get_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "size": len(self._cache),
            "keys": list(self._cache.keys()),
            "default_ttl": self._default_ttl
        }


# Global cache instance
_global_cache = SimpleCache(default_ttl=300)  # 5 minutes default


def get_cache() -> SimpleCache:
    """Get global cache instance"""
    return _global_cache


def cache_key(*args, **kwargs) -> str:
    """
    Generate cache key from function arguments

    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments

    Returns:
        MD5 hash of arguments as cache key
    """
    # Create deterministic string from args
    key_data = {
        "args": args,
        "kwargs": sorted(kwargs.items())
    }
    key_string = json.dumps(key_data, sort_keys=True, default=str)
    return hashlib.md5(key_string.encode()).hexdigest()


def cached(ttl: int = 300, key_prefix: str = ""):
    """
    Decorator to cache function results

    Args:
        ttl: Time-to-live in seconds
        key_prefix: Prefix for cache key

    Example:
        @cached(ttl=600, key_prefix="chapters")
        async def get_chapters():
            return await expensive_operation()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Check cache
            cache = get_cache()
            cached_value = cache.get(func_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = await func(*args, **kwargs)

            # Cache result
            cache.set(func_key, result, ttl=ttl)

            return result

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            func_key = f"{key_prefix}:{func.__name__}:{cache_key(*args, **kwargs)}"

            # Check cache
            cache = get_cache()
            cached_value = cache.get(func_key)
            if cached_value is not None:
                return cached_value

            # Execute function
            result = func(*args, **kwargs)

            # Cache result
            cache.set(func_key, result, ttl=ttl)

            return result

        # Return appropriate wrapper based on function type
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


# Export main components
__all__ = [
    "SimpleCache",
    "get_cache",
    "cached",
    "cache_key",
]
