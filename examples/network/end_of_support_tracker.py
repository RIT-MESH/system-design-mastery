"""End-of-support tracker (educational, std-lib only).

Tracks device end-of-support dates and flags devices approaching EOS.
Demonstrates firmware-lifecycle management at fleet scale.
Original for system-design-mastery.

Run:  python end_of_support_tracker.py
"""
from datetime import datetime, timedelta

DEVICES = [
    {"device": "fw1", "vendor": "Fortinet", "model": "FG-100F", "eos": datetime.now() + timedelta(days=60)},
    {"device": "sw1", "vendor": "Cisco", "model": "C9300", "eos": datetime.now() + timedelta(days=365)},
    {"device": "sw2", "vendor": "Aruba", "model": "2930F", "eos": datetime.now() + timedelta(days=15)},
    {"device": "r1", "vendor": "Yamaha", "model": "RTX830", "eos": datetime.now() + timedelta(days=200)},
    {"device": "ap1", "vendor": "Aruba", "model": "AP-515", "eos": datetime.now() - timedelta(days=5)},
]
WARN_DAYS = 90

def main():
    print(f"Tracking {len(DEVICES)} devices (warn at {WARN_DAYS} days before EOS):\n")
    for d in sorted(DEVICES, key=lambda x: x["eos"]):
        days = (d["eos"] - datetime.now()).days
        status = "UNSUPPORTED" if days < 0 else ("CRITICAL" if days <= 30 else ("WARNING" if days <= WARN_DAYS else "OK"))
        print(f"  {d['device']:8} {d['vendor']:10} {d['model']:10} EOS in {days:4} days  [{status}]")
    urgent = [d for d in DEVICES if (d["eos"] - datetime.now()).days <= WARN_DAYS]
    print(f"\n{len(urgent)} device(s) need upgrade planning within {WARN_DAYS} days.")

if __name__ == "__main__":
    main()
