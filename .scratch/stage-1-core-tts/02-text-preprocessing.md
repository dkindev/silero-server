---
title: "Stage 1.2: Text Preprocessing"
labels:
  - ready-for-agent
created: 2026-05-13
---

## What to build

Create `src/tts/text.py` as a deep, testable module for text preprocessing.

- `INPUT_TYPE=TEXT`: return text as-is
- `INPUT_TYPE=SSML`: strip XML tags, return plain text content
- `INPUT_TYPE=RAWMARYXML`: return None (caller emits 400 Bad Request)

Handle common SSML edge cases: nested tags, self-closing tags, text with `<>` characters.

## Acceptance criteria

- [ ] `preprocess_text("hello", "TEXT")` returns `"hello"`
- [ ] `preprocess_text("<speak>hello</speak>", "SSML")` returns `"hello"`
- [ ] `preprocess_text("hello <break/> world", "SSML")` returns `"hello  world"`
- [ ] `preprocess_text("< mary>", "TEXT")` returns `"< mary>"` (no stripping for TEXT)
- [ ] `preprocess_text("anything", "RAWMARYXML")` returns None
- [ ] Parametric unit tests cover all branches

## Blocked by

- Stage 1.1: TTS Config Pydantic Settings

