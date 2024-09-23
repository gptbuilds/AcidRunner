import time
import asyncio
import threading

class TokenBucket:
    _instance = None
    _lock = threading.Lock()  # Use threading.Lock for instance creation

    def __new__(cls, *args, **kwargs):
        # Singleton pattern with thread-safe lock (using threading.Lock)
        with cls._lock:
            if not cls._instance:
                cls._instance = super(TokenBucket, cls).__new__(cls)
        return cls._instance

    def __init__(self, capacity=10, refill_rate=0.5):
        if not hasattr(self, 'initialized'):  # Ensures init code runs only once
            self.capacity = capacity
            self.refill_rate = refill_rate
            self.current_tokens = capacity
            self.last_refill_time = time.time()
            self._token_lock = asyncio.Lock()  # Use asyncio.Lock for async safety in critical sections
            self.initialized = True

    async def configure(self, capacity=None, refill_rate=None):
        if capacity is not None:
            self.capacity = capacity
        if refill_rate is not None:
            self.refill_rate = refill_rate

    async def refill(self):
        now = time.time()
        elapsed = now - self.last_refill_time
        tokens_to_add = elapsed * self.refill_rate

        if tokens_to_add > 0:
            self.current_tokens = min(self.capacity, self.current_tokens + tokens_to_add)
            self.last_refill_time = now

    async def set_refill_rate(self, tpm):
        self.refill_rate = tpm / 60

    async def get_tokens(self, tokens_needed):
        await self.refill()
        async with self._token_lock:
            if tokens_needed <= self.current_tokens:
                self.current_tokens -= tokens_needed
                return True
            else:
                return False
