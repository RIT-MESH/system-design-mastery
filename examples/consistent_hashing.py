"""Consistent hashing simulation (educational, no third-party deps).

Demonstrates how consistent hashing keeps key movement low when nodes are added or removed,
compared to naive modulo hashing. Original implementation for system-design-mastery.

Run:  python consistent_hashing.py
"""
import hashlib


def _hash(s: str) -> int:
    return int(hashlib.sha256(s.encode()).hexdigest(), 16)


class ConsistentHashRing:
    """A ring with virtual nodes (vnodes) per real node to spread load evenly."""

    def __init__(self, vnodes: int = 150):
        self.vnodes = vnodes
        self.ring = {}  # hash -> node_id

    def add_node(self, node_id: str) -> None:
        for i in range(self.vnodes):
            h = _hash(f"{node_id}#{i}")
            self.ring[h] = node_id

    def remove_node(self, node_id: str) -> None:
        self.ring = {h: n for h, n in self.ring.items() if n != node_id}

    def node_for(self, key: str) -> str:
        h = _hash(key)
        # smallest hash >= h, else wrap to first
        for hashed in sorted(self.ring):
            if hashed >= h:
                return self.ring[hashed]
        return self.ring[min(self.ring)]


def naive_node(key: str, n_nodes: int) -> int:
    return _hash(key) % n_nodes


def simulate(keys, initial_nodes, ring):
    mapping = {k: ring.node_for(k) for k in keys}
    return mapping


def main() -> None:
    keys = [f"object-{i}" for i in range(10000)]
    ring = ConsistentHashRing(vnodes=150)
    for n in ["A", "B", "C", "D"]:
        ring.add_node(n)

    before = {k: ring.node_for(k) for k in keys}

    # Add a 5th node and measure how many keys move
    ring.add_node("E")
    moved_consistent = sum(1 for k in keys if ring.node_for(k) != before[k])

    # Naive modulo: adding a 5th node reassigns ~4/5 of keys
    naive_before = {k: naive_node(k, 4) for k in keys}
    naive_after = {k: naive_node(k, 5) for k in keys}
    moved_naive = sum(1 for k in keys if naive_after[k] != naive_before[k])

    print(f"keys: {len(keys)}")
    print(f"consistent hashing: keys moved after adding a node: {moved_consistent} "
          f"({moved_consistent / len(keys):.1%})  [expect ~1/5]")
    print(f"naive modulo hashing: keys moved after adding a node: {moved_naive} "
          f"({moved_naive / len(keys):.1%})  [expect ~4/5]")


if __name__ == "__main__":
    main()
