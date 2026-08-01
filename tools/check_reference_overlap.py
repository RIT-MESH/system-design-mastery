import sys
"""Check for text overlap with reference repositories.

Run:  python tools/check_reference_overlap.py --target . --reference ../ref1 --reference ../ref2
Does not modify files. Does not download anything.
"""
import os, sys, re, difflib

def read_paragraphs(path):
    paras = []
    for dp, dn, fn in os.walk(path):
        if ".git" in dp: continue
        for f in fn:
            if f.endswith(".md"):
                t = open(os.path.join(dp, f), encoding="utf-8-sig").read()
                for para in re.split(r"\n\n+", t):
                    para = para.strip()
                    if len(para) > 60:
                        paras.append(para)
    return paras

def main():
    args = sys.argv[1:]
    target = "."; refs = []
    i = 0
    while i < len(args):
        if args[i] == "--target": target = args[i+1]; i += 2
        elif args[i] == "--reference": refs.append(args[i+1]); i += 2
        else: i += 1
    if not refs:
        print("Usage: python check_reference_overlap.py --target . --reference ../ref1")
        sys.exit(1)
    target_paras = read_paragraphs(target)
    matches = 0
    for ref in refs:
        ref_paras = read_paragraphs(ref)
        for tp in target_paras:
            for rp in ref_paras:
                ratio = difflib.SequenceMatcher(None, tp[:200], rp[:200]).ratio()
                if ratio > 0.8:
                    print(f"HIGH SIMILARITY ({ratio:.0%}): {tp[:80]}...")
                    matches += 1
                elif ratio > 0.6:
                    print(f"MODERATE ({ratio:.0%}): {tp[:80]}...")
                    matches += 1
    if matches:
        print(f"\n{matches} potential overlap(s) found. Review and rewrite or attribute.")
        sys.exit(1)
    else:
        print("PASS: No high-similarity overlaps found.")
        sys.exit(0)

if __name__ == "__main__":
    main()
