from datetime import datetime, timedelta
from typing import Dict
import asyncio
import redis.asyncio as redis

class RateLimiter:
    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.window_size = 60  # 1 minute
        self.max_requests = 100  # per window
        
    async def check_rate_limit(self, client_id: str) -> Dict:
        """Check if request rate exceeds limits"""
        current_time = datetime.utcnow()
        window_key = f"rate_limit:{client_id}:{current_time.minute}"
        
        async with self.redis.pipeline() as pipe:
            try:
                # Increment request count
                await pipe.incr(window_key)
                # Set expiry if new key
                await pipe.expire(window_key, self.window_size)
                # Execute pipeline
                result = await pipe.execute()
                
                request_count = result[0]
                
                if request_count > self.max_requests:
                    return {
                        'limited': True,
                        'reset_time': current_time + timedelta(seconds=self.window_size),
                        'current_count': request_count
                    }
                    
                return {
                    'limited': False,
                    'current_count': request_count
                }
                
            except redis.RedisError as e:
                logging.error(f"Rate limiter error: {str(e)}")
                # Fail open to avoid blocking legitimate traffic
                return {'limited': False, 'error': str(e)}