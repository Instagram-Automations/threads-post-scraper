import time


class RateLimiter:
    def __init__(self, min_interval_ms: int = 250):
        self.min_interval = max(0, min_interval_ms) / 1000.0
        self._last = 0.0

    def wait(self):
        now = time.monotonic()
        delta = now - self._last
        if delta < self.min_interval:
            time.sleep(self.min_interval - delta)
        self._last = time.monotonic()
