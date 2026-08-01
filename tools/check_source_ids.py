import sys
"""Verify SOURCES.md IDs referenced in Markdown exist and are valid.

Run:  python tools/check_source_ids.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "node_modules", "work", "python-embed"}

def main():
    # Parse SOURCES.md for defined IDs
    sp = os.path.join(ROOT, "SOURCES.md")
    if not os.path.exists(sp):
        print("FAIL: SOURCES.md not found")
        sys.exit(1)
    st = open(sp, encoding="utf-8-sig").read()
    defined = set(re.findall(r"\b(S-[A-Z][A-Z0-9-]*)\b", st))
    if not defined:
        print("WARN: no S- IDs found in SOURCES.md")
    # Check references in all .md files
    issues = 0
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in SKIP): continue
        for f in fn:
            if not f.endswith(".md"): continue
            p = os.path.join(dp, f)
            t = open(p, encoding="utf-8-sig").read()
            refs = set(re.findall(r"\b(S-[A-Z][A-Z0-9-]*)\b", t))
            undefined = refs - defined
            if undefined and os.path.basename(p) != "SOURCES.md":
                rel = os.path.relpath(p, ROOT)
                print(f"FAIL {rel}: references undefined IDs: {undefined}")
                issues += 1
    # Check for duplicate IDs in SOURCES.md
    all_ids = re.findall(r"^\|\s*(S-[A-Z][A-Z0-9-]*)\s*\|", st, re.M)
    dupes = [x for x in all_ids if all_ids.count(x) > 1]
    if dupes:
        print(f"FAIL SOURCES.md: duplicate IDs: {set(dupes)}")
        issues += 1
    if issues:
        print(f"\n{issues} issue(s) found.")
        sys.exit(1)
    else:
        print(f"PASS: {len(defined)} source IDs defined, all references valid.")
        sys.exit(0)

if __name__ == "__main__":
    main()
