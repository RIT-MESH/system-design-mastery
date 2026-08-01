"""Queue + retry-with-jitter simulation (educational, no third-party deps).

Models a worker consuming from a queue with exponential backoff and jitter, plus a
poison-message/dead-letter policy after max attempts. Original implementation.

Run:  python queue_retry.py
"""
import random
import collections


def work(item: int, fail_rate: float) -> bool:
    return random.random() >= fail_rate


def main() -> None:
    random.seed(1)
    fail_rate = 0.4
    max_attempts = 3
    base_delay = 0.1  # not actually slept; used to compute schedule
    items = list(range(100))
    queue = collections.deque((it, 1) for it in items)  # (item, attempt)
    succeeded = 0
    dead_letters = 0
    while queue:
        item, attempt = queue.popleft()
        if work(item, fail_rate):
            succeeded += 1
            continue
        if attempt >= max_attempts:
            dead_letters += 1
            continue
        # exponential backoff with full jitter
        delay = random.uniform(0, base_delay * (2 ** (attempt - 1)))
        queue.append((item, attempt + 1))  # requeue (ordering simplified)
    print(f"items={len(items)} succeeded={succeeded} dead_letters={dead_letters}")
    print("dead-lettering prevents infinite retry; jitter spreads thundering herds.")


if __name__ == "__main__":
    main()
