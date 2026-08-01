# Diagrams

Original Mermaid diagrams for `system-design-mastery`. Every diagram is authored from the
accompanying written explanation and includes a `%% origin: original to system-design-mastery`
comment. No diagram is traced, recolored, renamed, or lightly modified from any reference.

## Layout
- `foundations/` — diagrams for Levels 0–1.
- `patterns/` — diagrams for Levels 2–9 (components, architecture, cloud, observability).
- `case-studies/` — diagrams for each case study, grouped by system name.

## Embedding
Diagrams are stored as `.mmd` source and embedded inline in the relevant chapter using a
```mermaid fenced block. The `.mmd` file is the source of truth; the inline copy must stay in
sync. GitHub renders ```mermaid blocks natively.

## Validation
The [mermaid-validate](../.github/workflows/mermaid-validate.yml) workflow renders every
`.mmd` file on push and pull request.
