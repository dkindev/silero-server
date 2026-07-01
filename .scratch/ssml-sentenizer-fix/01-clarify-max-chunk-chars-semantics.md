---
title: "Clarify max_chunk_chars semantics for SsmlSentenizer"
labels:
  - ready-for-agent
created: 2026-07-01
---

## Decision

`max_chunk_chars` in `SsmlSentenizer.text_to_sentences` limits **text content only**. Tags and the `<speak>...</speak>` wrapper are structural overhead — they do not count toward the limit.

This means a chunk like `<speak><p>hello</p></speak>` has `text_len=5` regardless of its total string length of 27. The embedded `PlainTextSentenizer` receives `max_chunk_chars` directly (no subtraction for wrapper or closing tags).

## Rationale

The test `test_ssml_splits_long_text_and_reopens_tags` at `tests/test_text_sentenizer.py:17` encodes this contract: it passes `max_chunk_chars=10` and expects chunks whose raw text (`"hello"`, `"world foo"`, `"bar baz"`) are all ≤ 10, even though the wrapped chunks (`<speak><p>hello</p></speak>`) are much larger. The old code subtracted `SPEAK_WRAPPER_LEN` (15) and closing-tag lengths from the text budget, treating `max_chunk_chars` as a total-size cap — this was inconsistent with the test.

## Impact

All callers of `SsmlSentenizer.text_to_sentences` pass `max_chunk_chars` as a raw-text budget. No caller needs adjustment. Downstream engine code (which passes this value from `--tts_max_chunk_chars`) is unaffected.
