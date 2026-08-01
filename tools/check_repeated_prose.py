import sys
"""Check for repeated boilerplate paragraphs across case studies.

Run:  python tools/check_repeated_prose.py
Exits 1 if repeated paragraphs found above a threshold.
"""
import os, re, collections

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = {".git", "node_modules", "work", "python-embed"}

def main():
    paragraphs = collections.defaultdict(list)
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in SKIP): continue
        for f in fn:
            if not f.endswith(".md"): continue
            if "case-studies" not in dp: continue
            t = open(os.path.join(dp, f), encoding="utf-8-sig").read()
            # Split into paragraphs (blocks separated by blank lines)
            for para in re.split(r"\n\n+", t):
                para = para.strip()
                if len(para) > 80:  # only check substantial paragraphs
                    rel = os.path.relpath(os.path.join(dp, f), ROOT)
                    paragraphs[para].append(rel)
    
    repeated = {p: files for p, files in paragraphs.items() if len(files) > 3}
    if repeated:
        print(f"FAIL: {len(repeated)} repeated paragraph(s) found in >3 files:")
        for p, files in list(repeated.items())[:10]:
            preview = p[:100].replace("\n", " ")
            print(f"  [{len(files)} files] {preview}...")
        # Count total affected files
        affected = set()
        for files in repeated.values():
            affected.update(files)
        print(f"\nTotal affected files: {len(affected)}")
        print("Fix: rewrite or remove the repeated paragraph to be case-specific.")
        sys.exit(1)
    else:
        print("PASS: No repeated paragraphs found in >3 case-study files.")
        sys.exit(0)

if __name__ == "__main__":
    main()
