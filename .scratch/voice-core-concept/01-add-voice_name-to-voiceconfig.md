---
title: "Add voice_name field to VoiceConfig and update Voice core concept in docs"
labels:
  - ready-for-agent
created: 2026-06-10
---
## What to build

Add `voice_name: str` to the `VoiceConfig` dataclass so the object carries its own name identifier. Pass the voice name through during YAML config loading. Update the Voice core concept in `CONTEXT.md` to:

- Document all four `VoiceConfig` fields (`voice_name`, `speaker`, `model`, `gender`)
- State that voice names are free format (remove the rigid `silero-{model}-{speaker}` naming convention)
- Add a YAML config example under the Voice section showing the fields

Update existing `VoiceConfig(...)` constructor calls across tests to include the new `voice_name=` keyword argument.

## Acceptance criteria

- [ ] `VoiceConfig` has a `voice_name: str` field (first position)
- [ ] YAML config loading passes the voice name into `VoiceConfig`
- [ ] All existing test `VoiceConfig(...)` calls include `voice_name=`
- [ ] `CONTEXT.md` Voice section documents the four fields and states names are free format
- [ ] `pytest tests/test_tts_models.py::TestVoiceConfig` passes

## Blocked by

None — can start immediately
