"""Token-bucket rate limiter simulation (educational, no third-party deps).

Shows a simple token bucket: tokens refill at a steady rate up to a capacity; each request
consumes a token; requests with no token are rejected. Original implementation.

Run:  python rate_limiter.py
"""
import time


class TokenBucket:
    def __init__(self, capacity: float, refill_per_second: float):
        self.capacity = capacity
        self.refill_per_second = refill_per_second
        self.tokens = capacity
        self.last = time.monotonic()

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_per_second)
        self.last = now

    def allow(self, cost: float = 1.0) -> bool:
        self._refill()
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False


def main() -> None:
    # 5 requests/sec sustained, burst of 10
    bucket = TokenBucket(capacity=10, refill_per_second=5)
    allowed = 0
    rejected = 0
    # Simulate 50 requests fired as fast as possible, then a pause.
    for i in range(50):
        if bucket.allow():
            allowed += 1
        else:
            rejected += 1
    print(f"burst: allowed={allowed} rejected={rejected} (burst exhausts the 10 tokens)")
    print("pausing 1s to refill ~5 tokens...")
    time.sleep(1.0)
    again_allowed = sum(1 for _ in range(20) if bucket.allow())
    print(f"after pause: allowed={again_allowed} of 20 (refill permits a short burst)")


if __name__ == "__main__":
    main()
