import sys
"""Validate case-study structure: 30 sections, status, Mermaid diagrams.

Run:  python tools/check_case_studies.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_SECTIONS = list(range(1, 31))

def main():
    issues = 0
    for tier in sorted(os.listdir(os.path.join(ROOT, "case-studies"))):
        d = os.path.join(ROOT, "case-studies", tier)
        if not os.path.isdir(d): continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"): continue
            p = os.path.join(d, fn)
            t = open(p, encoding="utf-8-sig").read()
            rel = f"{tier}/{fn}"
            # Check 30 sections
            found = set()
            for m in re.finditer(r"## (\d+)\.", t):
                found.add(int(m.group(1)))
            missing = [s for s in REQUIRED_SECTIONS if s not in found]
            if missing:
                print(f"FAIL {rel}: missing sections {missing}")
                issues += 1
            # Check status
            if "**Status:**" not in t:
                print(f"WARN {rel}: no Status field")
            # Check Mermaid count
            mc = t.count("```mermaid")
            if mc < 2:
                print(f"FAIL {rel}: only {mc} Mermaid blocks (need >=2)")
                issues += 1
            elif mc < 3 and tier in ("advanced", "extreme", "ai-systems", "network-ai-systems"):
                print(f"WARN {rel}: only {mc} Mermaid blocks (advanced/extreme need >=3)")
    if issues:
        print(f"\n{issues} issue(s) found.")
        sys.exit(1)
    else:
        print("PASS: All case studies have 30 sections and >=2 Mermaid blocks.")
        sys.exit(0)

if __name__ == "__main__":
    main()
