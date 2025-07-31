import hashlib
import json
import redis
import asyncio
from typing import List, Optional, Union
from datetime import timedelta
import logging
from .openai_service import CorrectionVariant

logger = logging.getLogger(__name__)

class CacheService:
    def __init__(self, redis_url: str = "redis://localhost:6379", default_ttl: int = 3600):
        self.redis_url = redis_url
        self.default_ttl = default_ttl
        self._redis_client = None
        self._fallback_cache = {}  # In-memory fallback when Redis is unavailable
        
    def _get_redis_client(self):
        if self._redis_client is None:
            try:
                self._redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
                # Test connection
                self._redis_client.ping()
            except Exception as e:
                logger.warning(f"Redis connection failed: {str(e)}. Using in-memory cache.")
                self._redis_client = None
        return self._redis_client
    
    def _generate_cache_key(self, text: str, model_name: str, correction_style: str = "default") -> str:
        """Generate a unique cache key for the correction request"""
        content = f"{text}|{model_name}|{correction_style}"
        return f"correction:{hashlib.sha256(content.encode()).hexdigest()[:16]}"
    
    async def get_cached_correction(
        self, 
        text: str, 
        model_name: str, 
        correction_style: str = "default"
    ) -> Optional[List[CorrectionVariant]]:
        """Get cached correction variants"""
        cache_key = self._generate_cache_key(text, model_name, correction_style)
        
        try:
            redis_client = self._get_redis_client()
            if redis_client:
                cached_data = await asyncio.to_thread(redis_client.get, cache_key)
                if cached_data:
                    variants_data = json.loads(cached_data)
                    return [
                        CorrectionVariant(
                            text=v['text'], 
                            type=v.get('type', 'correction'), 
                            reason=v['reason']
                        )
                        for v in variants_data
                    ]
            else:
                # Use fallback in-memory cache
                if cache_key in self._fallback_cache:
                    variants_data = self._fallback_cache[cache_key]
                    return [
                        CorrectionVariant(
                            text=v['text'], 
                            type=v.get('type', 'correction'), 
                            reason=v['reason']
                        )
                        for v in variants_data
                    ]
        except Exception as e:
            logger.error(f"Cache retrieval error: {str(e)}")
        
        return None
    
    async def cache_correction(
        self, 
        text: str, 
        model_name: str, 
        variants: List[CorrectionVariant],
        correction_style: str = "default",
        ttl: Optional[int] = None
    ) -> bool:
        """Cache correction variants"""
        cache_key = self._generate_cache_key(text, model_name, correction_style)
        ttl = ttl or self.default_ttl
        
        variants_data = [
            {"text": v.text, "type": v.type, "reason": v.reason}
            for v in variants
        ]
        
        try:
            redis_client = self._get_redis_client()
            if redis_client:
                await asyncio.to_thread(
                    redis_client.setex,
                    cache_key,
                    ttl,
                    json.dumps(variants_data, ensure_ascii=False)
                )
                return True
            else:
                # Use fallback in-memory cache with simple cleanup
                self._fallback_cache[cache_key] = variants_data
                # Keep only the last 100 entries to prevent memory bloat
                if len(self._fallback_cache) > 100:
                    oldest_key = next(iter(self._fallback_cache))
                    del self._fallback_cache[oldest_key]
                return True
        except Exception as e:
            logger.error(f"Cache storage error: {str(e)}")
            return False
    
    async def invalidate_cache(self, pattern: str = "correction:*") -> bool:
        """Invalidate cached corrections by pattern"""
        try:
            redis_client = self._get_redis_client()
            if redis_client:
                keys = await asyncio.to_thread(redis_client.keys, pattern)
                if keys:
                    await asyncio.to_thread(redis_client.delete, *keys)
                return True
            else:
                # Clear fallback cache
                self._fallback_cache.clear()
                return True
        except Exception as e:
            logger.error(f"Cache invalidation error: {str(e)}")
            return False
    
    async def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        try:
            redis_client = self._get_redis_client()
            if redis_client:
                info = await asyncio.to_thread(redis_client.info, "memory")
                keys_count = await asyncio.to_thread(redis_client.dbsize)
                return {
                    "type": "redis",
                    "keys_count": keys_count,
                    "memory_usage": info.get("used_memory_human", "unknown"),
                    "connected": True
                }
            else:
                return {
                    "type": "in_memory",
                    "keys_count": len(self._fallback_cache),
                    "memory_usage": "unknown",
                    "connected": False
                }
        except Exception as e:
            logger.error(f"Cache stats error: {str(e)}")
            return {
                "type": "error",
                "keys_count": 0,
                "memory_usage": "unknown",
                "connected": False,
                "error": str(e)
            }