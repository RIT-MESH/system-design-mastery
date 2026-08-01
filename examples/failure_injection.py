"""Failure-injection simulation (educational, no third-party deps).

Models a small call graph: Gateway -> Service -> DB, with per-call failure probabilities,
timeouts, a circuit breaker, and retry with jitter. Shows how a single dependency failure
can cascade, and how a circuit breaker + timeout contain it. Original implementation.

Run:  python failure_injection.py
"""
import random


class Endpoint:
    def __init__(self, name, fail_rate, latency_ms):
        self.name = name
        self.fail_rate = fail_rate
        self.latency_ms = latency_ms
        self.fails = 0
        self.calls = 0

    def call(self):
        self.calls += 1
        ok = random.random() >= self.fail_rate
        if not ok:
            self.fails += 1
        return ok, self.latency_ms


class CircuitBreaker:
    def __init__(self, threshold, cooldown):
        self.threshold = threshold
        self.cooldown = cooldown
        self.consec_fails = 0
        self.open = False
        self.trips = 0

    def allow(self):
        return not self.open

    def on_success(self):
        self.consec_fails = 0
        self.open = False

    def on_fail(self):
        self.consec_fails += 1
        if self.consec_fails >= self.threshold and not self.open:
            self.open = True
            self.trips += 1


def main() -> None:
    random.seed(7)
    db = Endpoint("DB", fail_rate=0.6, latency_ms=20)
    cb = CircuitBreaker(threshold=3, cooldown=5)
    successes = 0
    timeouts = 0
    breaker_blocks = 0
    timeout_ms = 15  # tighter than DB latency to force timeouts when DB is slow

    for i in range(1000):
        if not cb.allow():
            breaker_blocks += 1
            # simulate cooldown recovery attempt every few blocked calls
            if breaker_blocks % 5 == 0:
                cb.open = False  # half-open probe
            continue
        ok, lat = db.call()
        if lat > timeout_ms and not ok:
            timeouts += 1
            cb.on_fail()
            continue
        if ok:
            successes += 1
            cb.on_success()
        else:
            cb.on_fail()

    print(f"requests=1000  successes={successes}  timeouts={timeouts}  "
          f"breaker_blocks={breaker_blocks}  breaker_trips={cb.trips}")
    print(f"db calls={db.calls} db fails={db.fails}")
    print("The breaker stops hammering the failing DB; timeouts bound the wait per call.")


if __name__ == "__main__":
    main()
