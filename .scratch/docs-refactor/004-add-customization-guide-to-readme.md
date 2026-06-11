---
title: "Add customization guide to README"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Add a new "Customization" section to README.md covering how users can adapt the
server to their needs:

- Adding a new language (model entry + locale + voices in YAML)
- Adding or renaming voices (voice entries, optional `speaker` override)
- Disabling models (enabled: false) — voices are excluded automatically
- Tuning performance (TTS_MAX_MODELS, TTS_MAX_CONCURRENT_PER_MODEL,
TTS_MAX_CHUNK_CHARS)
- Selecting hardware (TTS_TORCH_DEVICE: cpu, cuda, xpu)
- Choosing sample rate (TTS_SAMPLE_RATE; engine auto-selects best match)
- Custom text preprocessing (subclass TextPreprocessor, register in deps.py)

## Acceptance criteria

- [ ] README.md has a "Customization" section with at least the topics above
- [ ] Each topic is actionable — a user can follow the instructions without
reading source code
- [ ] References to env vars link to the Environment Variables table
- [ ] CONTEXT.md is not modified by this issue

## Blocked by

None — can start immediately
