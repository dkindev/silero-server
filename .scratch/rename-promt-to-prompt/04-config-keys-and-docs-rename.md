---
title: "04 — Config key + documentation rename: promt → prompt"
labels:
  - ready-for-agent
created: 2026-07-14
---

## What to build

Update user-facing configuration keys and all documentation to use the corrected spelling "prompt".

Changes:
- `config.yml`: YAML key `promts:` → `prompts:`, commented-out key `# promts:` → `# prompts:`
- `CONTEXT.md`: `**Promt**` header → `**Prompt**`, all body references, remove the "intentional misspelling" entry from the Flagged ambiguities section
- `README.md`: Section heading `### Promts` → `### Prompts`, all field references (`promt_id` → `prompt_id`), YAML examples, table entries
- skip `.scratch/*`

## Acceptance criteria

- [x] `config.yml` keys renamed
- [x] `CONTEXT.md` term definition updated, flagged ambiguity removed
- [x] `README.md` section headings, field tables, and YAML examples updated
- [x] Scratch/planning documents updated
- [x] Whole test suite passes (regression check): `pytest -v`

## Blocked by

- #2 (Storage + config rename — ensures parser and config keys stay in sync)
