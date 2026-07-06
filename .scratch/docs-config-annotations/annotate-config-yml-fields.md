---
title: "Annotate config.yml fields with CLI/env references"
labels:
  - ready-for-agent
created: 2026-07-06
---

## What to build

Add multi-line comments to every field in config.yml documenting description, CLI argument name, and environment variable name.

Comment format per field:
```yaml
# Description of what this field does.
# CLI: --field_name
# Env: TTS_FIELD_NAME
field_name: value
```

Key details:
- CLI args for normalization fields are intentionally excluded (`_fields_to_skip` in `src/config.py:282`). For normalization fields, document as `# Env: TTS_NORMALIZATION__* (not available via CLI)` or omit CLI line.
- Env vars use `TTS_` prefix. Nested fields use double underscore: `TTS_NORMALIZATION__TIMEOUT`, `TTS_OPENAI__BASE_URL`.
- CLI args use underscore prefix: `--torch_device`, `--openai_base_url`, `--sample_rate`.
- Skip annotation for the multiline prompt text content in `normalization.text.promts` (it's data, not configuration).
- The `normalization` section in config.yml uses `normalization:` as the YAML key. The env var key is also `TTS_NORMALIZATION__*`.

## Acceptance criteria

- [x] Every config.yml field has a comment with description, CLI arg (or note that it's env/config only), and env var name
- [x] Prompt text content in `normalization.text.promts` is not annotated
- [x] YAML structure is valid after adding comments (parseable by pydantic-settings)
- [x] Comments are consistent in style across all fields

## Blocked by

None - can start immediately
