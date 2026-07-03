---
title: "Add Promt and VoiceNormalization entities + update CONTEXT.md"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Add two new frozen dataclasses to `src/tts/models.py`: `Promt` (reusable LLM prompt definition) and `VoiceNormalization` (per-voice, per-text-format override of normalization settings). Update `CONTEXT.md` with the new domain terms, relationships, example dialogue, and flagged ambiguity about the "promt" spelling.

## Acceptance criteria

- [x] `Promt` dataclass exists in `src/tts/models.py` with fields: `id: str`, `text: str`, `model: str`
- [x] `VoiceNormalization` dataclass exists in `src/tts/models.py` with fields: `voice_id: str`, `text_format: TextFormat`, `type: NormalizationType`, `enabled: bool`, `promt_id: str | None = None`
- [x] Both dataclasses are frozen
- [x] `CONTEXT.md` includes **VoiceNormalization** term with definition and `_Avoid_` alias
- [x] `CONTEXT.md` includes **Promt** term with definition and `_Avoid_` alias (noting misspelling convention)
- [x] `CONTEXT.md` includes relationships: Voice → VoiceNormalizations (zero or more), Promt → VoiceNormalizations (zero or more)
- [x] `CONTEXT.md` example dialogue includes a normalization override scenario
- [x] `CONTEXT.md` flagged ambiguities includes the "promt" spelling note

## Blocked by

None — can start immediately
