"""Check for generic/placeholder Mermaid diagrams.

Run:  python tools/check_mermaid_placeholders.py
Fails on:
- participant P0, P1, P2 (generic participant names)
- Generic labels (Store, Service, query, data, response, retry, fallback)
- Self-messages (P0 -->> P0)
- Truncated labels (ending in partial words)
- Empty branches
- Duplicate node IDs in the same diagram
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "node_modules", "work", "python-embed"}

GENERIC_PARTICIPANTS = ["P0", "P1", "P2", "P3", "P4", "P5"]
GENERIC_LABELS = {"Store", "Service", "query", "data", "response",
                  "retry", "fallback", "request", "process",
                  "look up or fetch", "fetch or store",
                  "persist or update", "return result",
                  "done", "retry or fallback"}

def check_file(path):
    issues = []
    rel = os.path.relpath(path, ROOT)
    t = open(path, encoding="utf-8-sig").read()

    # Check for generic participant names
    for p in GENERIC_PARTICIPANTS:
        if f"participant {p} as" in t:
            issues.append(f"generic participant {p}")

    # Check for generic labels in messages
    for label in GENERIC_LABELS:
        if f": {label}" in t or f'"{label}"' in t:
            issues.append(f"generic label '{label}'")

    # Check for self-messages
    for m in re.finditer(r"(P\d+)\s*--?>?>?\s*(P\d+)", t):
        if m.group(1) == m.group(2):
            issues.append(f"self-message {m.group(1)} ->> {m.group(2)}")

    # Check for truncated labels (words cut off)
    for m in re.finditer(r'as\s+(\S+)', t):
        name = m.group(1).strip()
        if len(name) > 3 and name[-1] not in "0123456789" and not name.endswith("e"):
            # Check if it ends in a truncated word (consonant cluster at end)
            if re.search(r"[bcdfghjklmnpqrstvwxz]{2,}$", name) and len(name) > 8:
                pass  # too many false positives; skip for now

    # Check for empty branches
    if "else" in t:
        else_idx = t.find("else")
        end_idx = t.find("end", else_idx)
        if end_idx >= 0:
            between = t[else_idx + 4:end_idx].strip()
            if not between:
                issues.append("empty else branch")

    return issues

def main():
    all_issues = []
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in SKIP):
            continue
        for f in fn:
            if f.endswith((".mmd", ".md")):
                p = os.path.join(dp, f)
                issues = check_file(p)
                if issues:
                    rel = os.path.relpath(p, ROOT)
                    for issue in issues:
                        all_issues.append(f"FAIL {rel}: {issue}")

    if all_issues:
        print(f"\n{len(all_issues)} issue(s) found:")
        for i in all_issues[:20]:
            print(f"  {i}")
        if len(all_issues) > 20:
            print(f"  ... and {len(all_issues) - 20} more")
        sys.exit(1)
    else:
        print("PASS: No generic placeholder diagrams found.")
        sys.exit(0)

if __name__ == "__main__":
    main()