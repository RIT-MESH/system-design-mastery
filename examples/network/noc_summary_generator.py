"""Daily NOC summary generator (educational, std-lib only).

Generates a daily NOC summary from simulated incident data: counts by
severity, top devices, and resolution status. Demonstrates report generation
for network operations.
Original for system-design-mastery.

Run:  python noc_summary_generator.py
"""
from collections import Counter

INCIDENTS = [
    {"id": 1, "severity": "critical", "device": "fw1", "status": "resolved", "duration_min": 45},
    {"id": 2, "severity": "critical", "device": "vpn-gw1", "status": "resolved", "duration_min": 120},
    {"id": 3, "severity": "high", "device": "core-r1", "status": "resolved", "duration_min": 30},
    {"id": 4, "severity": "high", "device": "sw3", "status": "open", "duration_min": 0},
    {"id": 5, "severity": "medium", "device": "dns1", "status": "resolved", "duration_min": 15},
    {"id": 6, "severity": "medium", "device": "fw1", "status": "resolved", "duration_min": 10},
    {"id": 7, "severity": "low", "device": "ap2", "status": "resolved", "duration_min": 5},
]

def main():
    sev = Counter(i["severity"] for i in INCIDENTS)
    status = Counter(i["status"] for i in INCIDENTS)
    devices = Counter(i["device"] for i in INCIDENTS)
    resolved = [i for i in INCIDENTS if i["status"] == "resolved"]
    mttr = sum(i["duration_min"] for i in resolved) / len(resolved) if resolved else 0

    print("=" * 50)
    print("  DAILY NOC SUMMARY")
    print("=" * 50)
    print(f"\n  Total incidents: {len(INCIDENTS)}")
    print(f"  By severity: {dict(sev)}")
    print(f"  By status: {dict(status)}")
    print(f"  Top devices: {devices.most_common(3)}")
    print(f"  MTTR (resolved): {mttr:.0f} min")
    print(f"\n  Open incidents: {status.get('open', 0)}")
    print("=" * 50)

if __name__ == "__main__":
    main()
