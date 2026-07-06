---
title: "Rewrite README configuration and domain sections"
labels:
  - ready-for-agent
created: 2026-07-06
---

## What to build

Update README.md to reflect actual project state. End-to-end documentation overhaul:

- **Description** (line 3): Replace with "Wyoming protocol TTS server wrapping Silero models. Supports Home Assistant integration, streaming audio, and optional per-voice LLM normalization."
- **Configuration section** (lines 56-132): Strip to 4-tier priority explanation + "See `config.yml` for full configuration reference with all fields, CLI argument names, and environment variable names." Remove CLI Arguments table, Environment Variables table, and config.yml example.
- **Voice and Model Configuration** (lines 134-183): Expand to full domain logic. Absorb content from Customization section:
  - Add normalization fields to voice fields table (`normalization.text.enabled`, `normalization.text.type`, `normalization.text.promt_id`, `normalization.ssml.*`)
  - Add `promts` subsection with fields table (`id`, `text`, `model`)
  - Update YAML example to include `normalization:` block and top-level `promts:` section
  - Add "Adding a new model", "Adding or renaming voices", "Disabling a model" sub-sections
- **Audio section** (replaces Wyoming Protocol, lines 185-206): Remove intro paragraph and "How it works" subsection. Keep only "Supported Input Types" (TEXT, SSML) and "Audio Output" (format, sample rate, bit depth, channels).
- **Remove Customization section** (lines 207-221) entirely.

## Acceptance criteria

- [x] Description matches approved text
- [x] Configuration section has no CLI/ENV tables or config.yml example
- [x] Voice and Model Configuration includes normalization fields, promts table, YAML examples, and model/voice management sub-sections
- [x] Audio section contains only input types and output specs
- [x] Customization section is removed
- [x] No broken markdown formatting

## Blocked by

None - can start immediately
