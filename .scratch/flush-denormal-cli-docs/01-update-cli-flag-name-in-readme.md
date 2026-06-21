---
title: "Update README CLI flag name for torch_flush_denormal"
labels:
  - ready-for-agent
created: 2026-06-21
---

## Parent

- `01-document-and-validate-streaming-config` (BooleanOptionalAction base change already done)

## What to build

Update the CLI Arguments table in README to reflect that `--torch_flush_denormal` now has a paired `--no-torch_flush_denormal` flag (from `BooleanOptionalAction` on all bool fields). This is a pure documentation change — the code already generates both flags.

## Acceptance criteria

- [x] README CLI Arguments table: `--torch_flush_denormal` → `--torch_flush_denormal / --no-torch_flush_denormal`

## Blocked by

- `01-document-and-validate-streaming-config` (BooleanOptionalAction code change)
