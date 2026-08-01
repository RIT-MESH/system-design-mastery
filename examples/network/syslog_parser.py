"""Syslog parser and severity classifier (educational, std-lib only).

Parses a syslog line into structured fields and classifies severity with a
small rule set. Demonstrates vendor-neutral normalization + severity mapping.

Run:  python syslog_parser.py
"""
import re

SAMPLES = [
    "<134>Oct 11 22:14:15 fw1.fortigate %%id=1 %%pri=1 %%src=10.0.0.1 %%msg=VPN tunnel down",
    "<134>Oct 11 22:14:16 core-r1 %%id=2 %%pri=4 %%msg=BGP neighbor 10.2.0.1 DOWN",
    "<134>Oct 11 22:14:17 sw3 %%id=3 %%pri=6 %%msg=Interface eth0 link flapping",
    "<165>Oct 11 22:14:18 dc1-dns %%id=4 %%msg=Failed to resolve example.com",
]

CRITICAL_PATTERNS = [
    ("VPN tunnel down", "critical", "VPN"),
    ("neighbor .* DOWN", "critical", "routing-neighbor"),
    ("link flapping", "high", "interface-flap"),
    ("Failed to resolve", "medium", "dns"),
]
PRI_TO_SEV = {0:"emergency",1:"alert",2:"critical",3:"error",4:"warning",5:"notice",6:"info",7:"debug"}

def parse(line):
    m = re.match(r"<(\d+)>(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(.*)", line)
    if not m:
        return None
    pri = int(m.group(1)); fac = pri >> 3; sev = pri & 7
    return {"facility": fac, "severity_code": sev, "severity": PRI_TO_SEV.get(sev,"?"),
            "ts": m.group(2), "device": m.group(3), "msg": m.group(4)}

def classify(msg):
    for pat, sev, cat in CRITICAL_PATTERNS:
        if re.search(pat, msg):
            return sev, cat
    return "info", "uncategorized"

def main():
    for s in SAMPLES:
        e = parse(s)
        if not e:
            print("unparseable:", s); continue
        sev, cat = classify(e["msg"])
        print(f"{e['device']:12} fac={e['facility']} pri_sev={e['severity']:9} -> rule_sev={sev:9} cat={cat:18} | {e['msg']}")
    print("\nRule-based classification; AI would refine categories and confidence.")

if __name__ == "__main__":
    main()
