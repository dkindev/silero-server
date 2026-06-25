---
title: "Fix sentenizer return types (string/None → list[str])"
labels:
  - ready-for-agent
created: 2026-06-25
---

## What to build

`SimpleTextSentenizer.text_to_sentences` and `SsmlSentenizer.text_to_sentences` return wrong types when input is short or empty:

- `SimpleTextSentenizer`: returns `text` (str) when `len(text) <= max_chunk_chars`, returns `None` when `not text`
- `SsmlSentenizer`: returns `ssml_text` (str) when `len(ssml_text) <= max_chunk_chars`

Both must always return `list[str]` as declared in the ABC. The engine iterates `for chunk in chunks` and a string return causes char-by-char iteration, producing audio chunks for each individual character.

### Changes

In `src/tts/preprocessing/text_sentenizer.py`:

- `SimpleTextSentenizer.text_to_sentences`: `if not text: return` → `if not text: return []`; `if len(text) <= max_chunk_chars: return text` → `if len(text) <= max_chunk_chars: return [text]`
- `SsmlSentenizer.text_to_sentences`: `if len(ssml_text) <= max_chunk_chars: return ssml_text` → `if len(ssml_text) <= max_chunk_chars: return [ssml_text]`
- Also `SsmlSentenizer.text_to_sentences`: add `if not text: return []` guard matching `SimpleTextSentenizer` (currently missing)

## Acceptance criteria

- [x] `SimpleTextSentenizer().text_to_sentences("", 100)` returns `[]`
- [x] `SimpleTextSentenizer().text_to_sentences("hello", 100)` returns `["hello"]`
- [x] `SsmlSentenizer(SimpleTextSentenizer()).text_to_sentences("", 100)` returns `[]`
- [x] `SsmlSentenizer(SimpleTextSentenizer()).text_to_sentences("<speak>hi</speak>", 100)` returns `["<speak>hi</speak>"]`
- [x] Type annotations match actual return types (no `str`/`None` leaks)

## Blocked by

None — can start immediately.
