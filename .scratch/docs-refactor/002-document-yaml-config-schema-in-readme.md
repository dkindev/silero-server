---
title: "Document YAML config schema in README"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Add a new "Configuration" section to README.md documenting the
`silero-to-mary-config.yml` schema. Include:

- Top-level structure: `models:`, `locales:`
- Each model field: name, language, enabled, warmup, hash_prefix
- Each locale entry: locale name, voices sub-key
- Each voice field: voice_name, speaker (optional), model, gender, locale
(injected)
- A full example config block

This content is currently in CONTEXT.md and should be moved to README, where
users configuring the server will find it.

## Acceptance criteria

- [ ] README.md has a "Configuration" section after "Environment Variables"
- [ ] Every YAML field has a description row (name, type, required/optional,
default)
- [ ] A complete example config is included
- [ ] CONTEXT.md is not modified by this issue

## Blocked by

None — can start immediately
