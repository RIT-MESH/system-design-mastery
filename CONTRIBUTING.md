# Contributing to system-design-mastery

Thank you for considering a contribution. This repository teaches system design, so the
quality, accuracy, and **originality** of every explanation matter more than volume. Please
read this document fully before opening a pull request.

## 1. Originality requirements (mandatory)

Every contribution must be **original** to this repository. Concretely:

- **Do not copy** wording, sentences, examples, capacity estimates, interview answers,
  tables, or diagrams from any other system-design repository, book, blog, or course.
- **Do not re-trace, re-color, rename, or lightly modify** diagrams from elsewhere.
- Mermaid diagrams must be constructed from your own written explanation and include an
  `%% origin: original to system-design-mastery` comment.
- A permissive license (e.g., MIT) on a source does **not** waive this originality rule; it
  only governs attribution. We aim higher than the minimum license allows.
- If a source has no clear license, treat it as **reference-only**: you may learn from it but
  must not reproduce or adapt its text or figures.

When you open a PR you assert: *"I wrote this contribution myself and did not copy text or
diagrams from any external source."*

## 2. Source and citation policy

- Back every non-trivial factual or technical claim with a citation in [SOURCES.md](SOURCES.md).
- Prefer **primary sources**: RFCs, academic papers, official vendor/cloud documentation,
  CNCF project docs, and database official docs. Secondary engineering blogs are acceptable
  with attribution; vendor marketing is not.
- Assign each new source a **stable ID** (e.g., `S-RFC8446`) in SOURCES.md and reference it by
  that ID in chapter "Further reading" sections.
- Quote minimally and only where a precise definition is required (e.g., an RFC term); always
  cite.

## 3. Chapter checklist

A chapter is mergeable only when all of the following are present:

- [ ] Clear learning objectives at the top.
- [ ] Original explanation with examples.
- [ ] Universal concept separated from vendor-specific implementations (where relevant).
- [ ] **Trade-offs** section.
- [ ] **When NOT to use this** section (where the concept is a pattern/choice).
- [ ] **Common mistakes** section.
- [ ] **Failure modes / operational concerns** section.
- [ ] **Review questions** section.
- [ ] **Further reading** section citing SOURCES.md IDs.
- [ ] **Previous / Next** navigation links.
- [ ] At least one original Mermaid diagram (where a diagram aids understanding).

## 4. Case-study checklist

Case studies must follow [templates/CASE-STUDY-TEMPLATE.md](templates/CASE-STUDY-TEMPLATE.md)
and include all 30 required sections, original Mermaid diagrams, and original traffic/storage/
bandwidth estimates. Do not reuse another system's numbers verbatim.

## 5. Diagram policy

- Author diagrams in Mermaid only. Store sources under `diagrams/<area>/` and embed in the
  chapter.
- Never include raster images traced from references.
- See the [diagram originality policy](../work/RESEARCH-REPORT.md#11-diagram-originality-policy).

## 6. Style and terminology

- Use consistent terminology (see [GLOSSARY.md](GLOSSARY.md)). When introducing a term, link
  to its glossary entry on first use.
- Keep beginner chapters free of artificial complexity; introduce advanced nuance gradually.
- Avoid presenting any one architecture as universally correct; present alternatives.
- Plain, precise English. Prefer short paragraphs and bullets for lists.

## 7. Development workflow

1. Pick an item from [BACKLOG.md](BACKLOG.md) (or open an issue first).
2. Create a branch named `add/<level>-<topic>` or `add/case-study-<name>`.
3. Write content following the checklists above.
4. Run the validation workflows locally (see `.github/workflows/`):
   - `npx markdownlint-cli2 '**/*.md'`
   - `lychee --no-progress '**/*.md'` (link check)
   - `mmdc` Mermaid render check on `.mmd` files (or rely on CI).
5. Open a PR against `main` using [`.github/PULL_REQUEST_TEMPLATE.md`](.github/PULL_REQUEST_TEMPLATE.md).

## 8. Review model

Two reviewers per content PR where feasible:

- **Technical reviewer**: accuracy, trade-offs, failure modes, capacity math correctness.
- **Editorial reviewer**: clarity, terminology consistency, navigation, style.
- A reviewer checks the originality statement and spot-checks against references where
  suspicious.

## 9. Code contributions

- Python simulations go under `examples/` and must be runnable with `python3 <file>.py` and
  have no third-party dependencies unless approved.
- Calculators/worksheets may be Python scripts or Markdown templates in `calculations/`.
- Keep code minimal and educational; comment the non-obvious parts.

## 10. Licensing

By contributing you agree your content is licensed under CC BY 4.0 (prose/diagrams) and MIT
(code), as described in [LICENSE](LICENSE).

## 11. Code of Conduct

All interactions are governed by the [Code of Conduct](CODE_OF_CONDUCT.md). Be respectful,
constructive, and assume good intent.
