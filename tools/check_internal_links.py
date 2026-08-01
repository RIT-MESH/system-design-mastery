import sys
"""Verify all internal Markdown links resolve to existing files.

Run:  python tools/check_internal_links.py
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "node_modules", "work", "python-embed"}

def main():
    md_files = []
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in SKIP): continue
        for f in fn:
            if f.endswith(".md"): md_files.append(os.path.join(dp, f))
    bad = 0; total = 0
    for p in md_files:
        t = open(p, encoding="utf-8-sig").read()
        for m in re.finditer(r"\[([^\]]+)\]\(([^)]+)\)", t):
            link = m.group(2).split("#")[0].split(" ")[0]
            if not link or link.startswith(("http://", "https://", "mailto:")): continue
            total += 1
            base = os.path.dirname(p)
            target = os.path.normpath(os.path.join(base, link))
            if not os.path.exists(target):
                rel = os.path.relpath(p, ROOT)
                print(f"BROKEN [{rel}] -> {link}")
                bad += 1
    if bad:
        print(f"\nFAIL: {bad} broken link(s) out of {total} checked.")
        sys.exit(1)
    else:
        print(f"PASS: {total} internal links checked, 0 broken.")
        sys.exit(0)

if __name__ == "__main__":
    main()
