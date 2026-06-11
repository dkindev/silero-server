---
title: "Document hash_prefix field in Model concept"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Update CONTEXT.md to document the new `hash_prefix` field on the Model domain concept.

Two changes in CONTEXT.md:

1. **YAML example** — Add `hash_prefix: a1b2c3d4` to the `v5_5_ru` model entry to show users how to configure it.

2. **Field list** — Add `hash_prefix` as the last entry in the Model field list (after `warmup`):

   > **`hash_prefix`** — Optional SHA-256 hash prefix for download integrity verification. When set, the downloaded model file must match this prefix; omitted or empty skips verification.

No code changes — all implementation and tests were completed in the parent issue.

## Acceptance criteria

- [x] YAML example in Model section shows `hash_prefix` on `v5_5_ru`
- [x] Model field list includes `hash_prefix` as the last entry with correct domain-level description
- [x] All existing documentation stays intact

## Blocked by

- [01-add-hash-prefix-to-model.md](.scratch/model-hash-prefix/01-add-hash-prefix-to-model.md) — parent issue, implementation completed
