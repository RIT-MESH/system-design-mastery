"""Firmware inventory scanner (educational, std-lib only).

Scans a simulated device inventory and reports firmware versions, end-of-support
status, and devices needing upgrades. Demonstrates fleet firmware tracking.
Original for system-design-mastery.

Run:  python firmware_inventory_scanner.py
"""
INVENTORY = [
    {"device": "fw1", "vendor": "Fortinet", "model": "FG-100F", "firmware": "7.4.1", "target": "7.4.3", "advisories": 2},
    {"device": "sw1", "vendor": "Cisco", "model": "C9300", "firmware": "17.6.1", "target": "17.9.2", "advisories": 0},
    {"device": "sw2", "vendor": "Aruba", "model": "2930F", "firmware": "16.02", "target": "16.11", "advisories": 3},
    {"device": "r1", "vendor": "Yamaha", "model": "RTX830", "firmware": "14.01.20", "target": "14.01.26", "advisories": 1},
    {"device": "ap1", "vendor": "Aruba", "model": "AP-515", "firmware": "10.4", "target": "10.4", "advisories": 0},
]

def main():
    print(f"Firmware inventory: {len(INVENTORY)} devices\n")
    print(f"{'Device':8} {'Vendor':10} {'Current':12} {'Target':12} {'Adv':4} {'Status'}")
    print("-" * 65)
    for d in INVENTORY:
        needs = d["firmware"] != d["target"]
        status = "UP-TO-DATE" if not needs else ("URGENT" if d["advisories"] > 0 else "UPDATE AVAILABLE")
        print(f"{d['device']:8} {d['vendor']:10} {d['firmware']:12} {d['target']:12} {d['advisories']:4} {status}")
    urgent = [d for d in INVENTORY if d["firmware"] != d["target"] and d["advisories"] > 0]
    print(f"\n{len(urgent)} device(s) with open advisories need immediate upgrade.")

if __name__ == "__main__":
    main()
