"""
Caching Utilities
Sustainable Economic Development Analytics Hub
Ministry of Economy and Planning

Simple in-memory caching for frequently accessed data.
Designed to be replaced with Redis or similar in production.
"""

from typing import Any, Optional, Dict, Callable
from datetime import datetime, timedelta
from functools import wraps
import hashlib
import json

from analytics_hub_platform.infrastructure.settings import get_settings


class CacheEntry:
    """A single cache entry with expiration."""
    
    def __init__(self, value: Any, ttl_seconds: int):
        self.value = value
        self.created_at = datetime.now()
        self.expires_at = self.created_at + timedelta(seconds=ttl_seconds)
    
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        return datetime.now() > self.expires_at


class CacheManager:
    """
    Simple in-memory cache manager.
    
    Features:
    - TTL-based expiration
    - Automatic cleanup of expired entries
    - Thread-safe for basic operations
    
    Extension Point: Replace with Redis client for production deployment.
    """
    
    def __init__(self, default_ttl: int = 300, enabled: bool = True):
        """
        Initialize cache manager.
        
        Args:
            default_ttl: Default time-to-live in seconds
            enabled: Whether caching is enabled
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._enabled = enabled
        self._hits = 0
        self._misses = 0
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached value or None if not found/expired
        """
        if not self._enabled:
            return None
        
        entry = self._cache.get(key)
        
        if entry is None:
            self._misses += 1
            return None
        
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        self._hits += 1
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Optional TTL override in seconds
        """
        if not self._enabled:
            return
        
        ttl = ttl or self._default_ttl
        self._cache[key] = CacheEntry(value, ttl)
    
    def delete(self, key: str) -> bool:
        """
        Delete a key from cache.
        
        Args:
            key: Cache key
            
        Returns:
            True if key existed, False otherwise
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cached entries."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired entries.
        
        Returns:
            Number of entries removed
        """
        expired_keys = [k for k, v in self._cache.items() if v.is_expired()]
        for key in expired_keys:
            del self._cache[key]
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total = self._hits + self._misses
        hit_rate = (self._hits / total * 100) if total > 0 else 0
        
        return {
            "enabled": self._enabled,
            "entries": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(hit_rate, 2),
        }


def make_cache_key(*args, **kwargs) -> str:
    """
    Generate a cache key from function arguments.
    
    Args:
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        MD5 hash string as cache key
    """
    key_data = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True, default=str)
    return hashlib.md5(key_data.encode()).hexdigest()


def cached(ttl: Optional[int] = None, key_prefix: str = ""):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Optional TTL override in seconds
        key_prefix: Optional prefix for cache keys
        
    Example:
        @cached(ttl=300, key_prefix="summary")
        def get_summary(tenant_id: str, year: int):
            ...
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            cache = get_cache()
            
            # Build cache key
            func_key = f"{key_prefix}:{func.__name__}" if key_prefix else func.__name__
            args_key = make_cache_key(*args, **kwargs)
            cache_key = f"{func_key}:{args_key}"
            
            # Try cache
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator


# Global cache instance
_cache_instance: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """
    Get the global cache manager instance.
    
    Returns:
        CacheManager instance
    """
    global _cache_instance
    if _cache_instance is None:
        settings = get_settings()
        _cache_instance = CacheManager(
            default_ttl=settings.cache_ttl_seconds,
            enabled=settings.cache_enabled,
        )
    return _cache_instance
