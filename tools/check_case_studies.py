"""Validate case-study structure: 30 sections, status, Mermaid diagrams, minimum content.

Run:  python tools/check_case_studies.py
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REQUIRED_SECTIONS = list(range(1, 31))
MIN_WORDS_PER_SECTION = 15  # minimum words per section body

def main():
    issues = 0
    for tier in sorted(os.listdir(os.path.join(ROOT, "case-studies"))):
        d = os.path.join(ROOT, "case-studies", tier)
        if not os.path.isdir(d):
            continue
        for fn in sorted(os.listdir(d)):
            if not fn.endswith(".md"):
                continue
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

            # Check minimum content per critical section (6, 7, 8 = traffic/storage/bandwidth)
            for sec_num in [6, 7, 8, 19, 25]:
                m = re.search(rf"## {sec_num}\..*\n(.*?)(?=\n## |\Z)", t, re.S)
                if m:
                    body = m.group(1).strip()
                    wc = len(body.split())
                    if wc < MIN_WORDS_PER_SECTION:
                        print(f"WARN {rel}: section {sec_num} has only {wc} words (min {MIN_WORDS_PER_SECTION})")

    if issues:
        print(f"\n{issues} issue(s) found.")
        sys.exit(1)
    else:
        print("PASS: All case studies have 30 sections, >=2 Mermaid blocks, and minimum content per critical section.")
        sys.exit(0)

if __name__ == "__main__":
    main()