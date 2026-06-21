---
title: "Document and validate streaming configuration"
labels:
  - ready-for-agent
created: 2026-06-21
---

## What to build

Fix the `streaming` field definition in Settings and add it to the README documentation.

The `streaming` field currently uses `default="true"` (string) instead of `default=True` (bool), and the CLI generation uses `store_true` with no way to disable via CLI (`--no-streaming`). Add `BooleanOptionalAction` for bool CLI args. Update the field description. Add tests covering default, env var, and CLI behavior. Add the field to README tables.

## Acceptance criteria

- [x] `streaming` field default changed from `"true"` (string) to `True` (bool)
- [x] Field description changed from `"Audio streaming support. Set to a false to disable."` to `"Enable audio streaming"`
- [x] Bool CLI args use `BooleanOptionalAction` instead of `store_true` — generates both `--streaming` and `--no-streaming`
- [x] Test: default value is `True`
- [x] Test: `TTS_STREAMING=false` env var overrides to `False`
- [x] README CLI Arguments table includes `--streaming / --no-streaming` row
- [x] README Environment Variables table includes `TTS_STREAMING` row
- [x] README config.yml example includes `streaming: true`
- [x] `pytest tests/` passes

## Blocked by

None - can start immediately
