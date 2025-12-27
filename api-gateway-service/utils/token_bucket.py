import time
import asyncio
from dataclasses import dataclass # Ensure the 'es' is present

@dataclass
class Bucket:
    tokens: float
    updated_at: float

class TokenBucketManager:
    def __init__(self, rate: float, capacity: int):
        self.rate = rate
        self.capacity = capacity
        self.buckets = {}
        self.lock = asyncio.Lock()
    
    async def consume(self, key: str) -> bool:
        # Enforce Atomicity to prevent 'Double Spending' of tokens
        async with self.lock:
            now = time.time()
            
            # Initialization and Retrieval in one step
            if key not in self.buckets:
                self.buckets[key] = Bucket(self.capacity, now)
            
            bucket = self.buckets[key]

            # Lazy Evaluation: Calculate 'earned' tokens since last arrival
            elapsed = now - bucket.updated_at
            refill = elapsed * self.rate
            
            # Homeostasis: Ensure we don't exceed the burst capacity
            bucket.tokens = min(self.capacity, bucket.tokens + refill)
            bucket.updated_at = now

            # Conformance Check
            if bucket.tokens >= 1:
                bucket.tokens -= 1
                return True
            return False