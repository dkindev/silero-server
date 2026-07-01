---
title: "Adopt RuPlainTextSentenizer tests to Iterator[str] return type"
labels:
  - ready-for-agent
created: 2026-07-01
---

## What to build

`RuPlainTextSentenizer.text_to_sentences()` now returns `Iterator[str]` instead of `list[str]`. The tests in `test_ru_text_sentenizer.py` compare the return value directly to lists via `assert chunks == [...],` which will always fail for an iterator.

Wrap each `text_to_sentences(...)` call with `list(...)` so the test assertions compare a concrete list to the expected list.

## Acceptance criteria

- [x] All 7 assertions in `TestRuSimpleTextSentenizer` pass with the Iterator return type
- [x] `chunks` variable is wrapped with `list(...)` when `text_to_sentences` returns an iterator
- [x] No changes to production source code

## Blocked by

None — can start immediately.
