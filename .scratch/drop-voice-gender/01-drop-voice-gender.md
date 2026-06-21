---
title: "Drop gender from Voice model, config, tests, and docs"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Remove the unused `gender` field from the `Voice` dataclass and all references to it across the codebase. The field is parsed from YAML config but never used in synthesis, Wyoming protocol serialization, or any business logic — pure dead code.

Changes span all layers:

- **Schema**: remove `gender: str` from the `Voice` frozen dataclass
- **Config parsing**: remove `gender=voice_entry.get("gender", "")` from YAML config loading in config storage. Existing configs that still have a `gender:` key are silently ignored (PyYAML naturally drops unknown dict keys).
- **Tests**: remove `gender=` arguments from all `Voice()` constructor calls, remove gender assertions, and remove `gender:` from inline YAML test strings
- **Documentation**: remove `{gender}` from the `/voices` response format, `gender:` from YAML examples, and the `gender` row from the voice field table in README.md

## Acceptance criteria

- [x] `Voice` dataclass has no `gender` field
- [x] Config loading silently skips `gender` key in YAML voice entries
- [x] All existing tests pass (`pytest tests/`)
- [x] All lint/format checks pass (`ruff check src tests`)
- [x] README.md has no references to `gender`

## Blocked by

None — can start immediately
