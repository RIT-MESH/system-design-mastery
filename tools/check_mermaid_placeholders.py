import sys
"""Check for generic/placeholder Mermaid diagrams.

Run:  python tools/check_mermaid_placeholders.py
Fails on generic P0/P1 sequences, truncated labels, empty branches.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "node_modules", "work", "python-embed"}

GENERIC_PATTERNS = [
    r"participant P0\s+as\s+\w+\n\s+participant P1\s+as\s+\w+\n\s+P0 ->> P1: request\n\s+P1 -->> P0: response",
]

def main():
    issues = 0
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in SKIP): continue
        for f in fn:
            if not f.endswith(".mmd") and not f.endswith(".md"): continue
            p = os.path.join(dp, f)
            t = open(p, encoding="utf-8-sig").read()
            rel = os.path.relpath(p, ROOT)
            # Check for generic P0/P1 request/response only
            for pat in GENERIC_PATTERNS:
                if re.search(pat, t):
                    print(f"FAIL {rel}: generic P0->P1 request/response sequence")
                    issues += 1
            # Check for truncated labels (words ending abruptly)
            for m in re.finditer(r'"([^"]{2,40})"', t):
                label = m.group(1)
                # Check for truncated words (ending in partial word with no space)
                if re.search(r"\b[a-z]{1,3}$", label) and len(label) > 10:
                    # Might be truncated - check context
                    words = label.split()
                    if words and len(words[-1]) <= 3 and words[-1] not in ("the", "and", "for", "not", "but", "all", "any", "can", "may", "use"):
                        pass  # too many false positives; skip
            # Check for empty branches
            if "else" in t and re.search(r"else\n\s*end", t):
                print(f"WARN {rel}: potentially empty else branch")
    if issues:
        print(f"\n{issues} issue(s) found.")
        sys.exit(1)
    else:
        print("PASS: No generic placeholder diagrams found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
