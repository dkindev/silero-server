---
title: "Add Voice availability rule to CONTEXT.md"
labels:
  - ready-for-agent
created: 2026-06-11
---

## Parent

- /workspaces/python/.scratch/locale-voice-restructure/04-exclude-locales-without-usable-voices.md

## What to build

Add a Voice availability rule to CONTEXT.md, making explicit what the code already enforces: a voice is available in the API only when its referenced model is enabled and its locale survives filtering (has at least one voice on an enabled model).

### Specific changes to CONTEXT.md

**Voice section** — insert a new paragraph after the YAML example (after the block, before the field descriptions):

> A voice is available in the API only when its referenced model is enabled and the locale survives filtering (has at least one voice on an enabled model). Voices whose model is disabled, or whose locale has no remaining enabled voices, are excluded from `get_voices()`, `has_voice()`, and the `/voices` endpoint.

**Locale section** — update the existing note (current line 62) to cross-reference the Voice rule:

> A locale is included in the supported set only when at least one of its voices references an enabled model (see Voice availability rule). Locales with no voices, or whose voices all reference disabled or undefined models, are excluded.

## Acceptance criteria

- [x] Voice section contains a paragraph stating the availability rule: voice needs enabled model + surviving locale
- [x] Locale section's availability note cross-references the Voice rule
- [x] All field descriptions and YAML examples remain untouched and accurate
- [x] `CONTEXT.md` renders correctly as markdown

## Blocked by

- /workspaces/python/.scratch/locale-voice-restructure/04-exclude-locales-without-usable-voices.md
