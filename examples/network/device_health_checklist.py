"""Device-health checklist (educational, std-lib only).

Runs a set of health checks against a simulated device and reports pass/fail.
Demonstrates pre-upgrade and post-upgrade validation checklists.
Original for system-design-mastery.

Run:  python device_health_checklist.py
"""
CHECKS = [
    ("Management reachable", True),
    ("Control plane healthy (BGP up)", True),
    ("Data plane: key paths OK", True),
    ("CPU < 70 percent", False),
    ("Memory < 80 percent", True),
    ("No new critical syslog (last 5 min)", True),
    ("HA peer in sync", True),
    ("Config matches baseline", False),
]

def main():
    print("Device: core-r1  (post-upgrade validation)\n")
    passed = 0
    for name, ok in CHECKS:
        status = "PASS" if ok else "FAIL"
        if ok: passed += 1
        print(f"  [{status}] {name}")
    print(f"\n{passed}/{len(CHECKS)} checks passed.")
    if passed < len(CHECKS):
        print("VALIDATION FAILED -> trigger rollback.")
    else:
        print("VALIDATION PASSED -> upgrade successful.")

if __name__ == "__main__":
    main()
