"""Repository statistics generator for system-design-mastery.

Run:  python tools/repository_stats.py
Prints a Markdown-compatible statistics table. Use --update-readme to update
the generated section in README.md automatically.
"""
import os, sys, statistics, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def count_files():
    skip = {".git", "node_modules", "work", "python-embed"}
    total = md = py = mmd = inline_mermaid = 0
    case_dirs = 0; case_md = 0
    word_counts = []
    complete = draft = 0
    for dp, dn, fn in os.walk(ROOT):
        if any(s in dp for s in skip): continue
        for f in fn:
            total += 1
            if f.endswith(".md"):
                md += 1
                p = os.path.join(dp, f)
                t = open(p, encoding="utf-8-sig").read()
                inline_mermaid += t.count("```mermaid")
                # Check if it's a case study
                rel = os.path.relpath(p, ROOT)
                if rel.startswith("case-studies" + os.sep):
                    wc = len(t.split())
                    word_counts.append(wc)
                    case_md += 1
                    if "**Status:** complete" in t: complete += 1
                    elif "**Status:** draft" in t: draft += 1
            elif f.endswith(".py"): py += 1
            elif f.endswith(".mmd"): mmd += 1
    for d in os.listdir(os.path.join(ROOT, "case-studies")):
        if os.path.isdir(os.path.join(ROOT, "case-studies", d)): case_dirs += 1
    med = int(statistics.median(word_counts)) if word_counts else 0
    mn = min(word_counts) if word_counts else 0
    mx = max(word_counts) if word_counts else 0
    return {"total_files": total, "md_files": md, "py_files": py, "mmd_files": mmd,
            "inline_mermaid": inline_mermaid, "case_dirs": case_dirs, "case_md": case_md,
            "median_words": med, "min_words": mn, "max_words": mx,
            "complete": complete, "draft": draft}

def main():
    s = count_files()
    print("| Metric | Value |")
    print("|--------|-------|")
    for k, v in s.items():
        print(f"| {k} | {v} |")
    if "--update-readme" in sys.argv:
        update_readme(s)

def update_readme(s):
    rp = os.path.join(ROOT, "README.md")
    t = open(rp, encoding="utf-8-sig").read()
    block = f"""<!-- BEGIN GENERATED REPOSITORY STATS -->
| Metric | Value |
|--------|-------|
| Total files | {s['total_files']} |
| Markdown files | {s['md_files']} |
| Python files | {s['py_files']} |
| Standalone .mmd files | {s['mmd_files']} |
| Inline Mermaid blocks | {s['inline_mermaid']} |
| Case-study directories | {s['case_dirs']} |
| Case-study Markdown files | {s['case_md']} |
| Median case-study word count | {s['median_words']} |
| Min case-study word count | {s['min_words']} |
| Max case-study word count | {s['max_words']} |
| Complete case studies | {s['complete']} |
| Draft case studies | {s['draft']} |
<!-- END GENERATED REPOSITORY STATS -->"""
    pattern = r"<!-- BEGIN GENERATED REPOSITORY STATS -->.*?<!-- END GENERATED REPOSITORY STATS -->"
    if re.search(pattern, t, re.S):
        t = re.sub(pattern, block, t, flags=re.S)
    else:
        t = t.rstrip() + "\n\n" + block + "\n"
    open(rp, "w", encoding="utf-8", newline="\n").write(t)
    print("\nREADME.md updated with generated stats.")

if __name__ == "__main__":
    main()
