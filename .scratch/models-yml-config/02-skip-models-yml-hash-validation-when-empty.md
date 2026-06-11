---
title: "Skip models.yml hash validation when hash is empty"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

When `TTS_MODELS_YML_HASH` is empty (unset, `""`, or whitespace-only after stripping), skip SHA-256 hash verification during `models.yml` download. If a non-empty hash is provided that is not a valid 64-character lowercase hex string, reject it at Settings validation startup with a clear error.

### Details from prototyping session

**Boundary for "empty":** `None` or `""` after strip → skip validation. A non-empty hash that doesn't match `^[a-f0-9]{64}$` raises a `ValueError` at Settings construction.

**Engine behavior change:** When `models_yml_hash` is `None` or empty in `_get_models_data()`, skip the hash comparison on existing file and skip hash verification after download in `_download_models_yml()`.

## Acceptance criteria

- [x] Setting `TTS_MODELS_YML_HASH=""` skips hash validation and download succeeds
- [x] Unset `TTS_MODELS_YML_HASH` (default hash) still performs full verification
- [x] Setting `TTS_MODELS_YML_HASH` to a non-64-char hex string raises a startup validation error
- [x] Tests cover all three cases: empty skips, invalid hash fails startup, valid hash enables verification

## Blocked by

- `01-migrate-models-yml-url-and-hash-to-env-config` (must complete first — this slice builds on the config plumbing)
