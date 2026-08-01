"""Certificate-expiry monitor (educational, std-lib only).

Scans a list of certificates (simulated) and flags those expiring within a
warning window. Demonstrates proactive cert management for network devices.
Original for system-design-mastery.

Run:  python certificate_expiry_monitor.py
"""
from datetime import datetime, timedelta

CERTS = [
    {"device": "fw1.fortigate", "cn": "*.corp.local", "expiry": datetime.now() + timedelta(days=10)},
    {"device": "core-r1", "cn": "router1.corp.local", "expiry": datetime.now() + timedelta(days=45)},
    {"device": "vpn-gw1", "cn": "vpn.corp.local", "expiry": datetime.now() + timedelta(days=3)},
    {"device": "lb1", "cn": "lb.corp.local", "expiry": datetime.now() + timedelta(days=90)},
    {"device": "sw-core", "cn": "switch.corp.local", "expiry": datetime.now() + timedelta(days=25)},
]
WARN_DAYS = 30

def main():
    print(f"Checking {len(CERTS)} certificates (warn at {WARN_DAYS} days):\n")
    for c in sorted(CERTS, key=lambda x: x["expiry"]):
        days = (c["expiry"] - datetime.now()).days
        status = "CRITICAL" if days <= 7 else ("WARNING" if days <= WARN_DAYS else "OK")
        print(f"  {c['device']:18} {c['cn']:25} expires in {days:3} days  [{status}]")
    expired = [c for c in CERTS if (c["expiry"] - datetime.now()).days <= WARN_DAYS]
    print(f"\n{len(expired)} certificate(s) need renewal within {WARN_DAYS} days.")

if __name__ == "__main__":
    main()
