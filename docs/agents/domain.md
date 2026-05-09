# Domain Docs

## Layout

**Single-context** — One `CONTEXT.md` at the repo root, with ADRs in `docs/adr/`.

## Consumer Rules

The following skills read these files:

- `improve-codebase-architecture` — reads `CONTEXT.md` to learn the domain language, reads `docs/adr/` for architectural decisions
- `diagnose` — reads `CONTEXT.md` for context on the codebase
- `tdd` — reads `CONTEXT.md` to understand domain concepts

## Expected Files

- `./CONTEXT.md` — project overview, domain terminology, key concepts
- `./docs/adr/` — architectural decision records (optional but recommended)

If `CONTEXT.md` doesn't exist yet, skills will note its absence but continue working.