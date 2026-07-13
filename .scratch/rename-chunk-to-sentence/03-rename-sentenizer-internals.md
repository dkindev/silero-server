---
title: "Rename sentenizer internals from chunk to sentence terminology"
labels:
  - ready-for-agent
created: 2026-07-13
---

## What to build

Rename internal identifiers in the plain text and SSML sentenizers that use "chunk" terminology to use "sentence" instead. This is purely mechanical — no behavior changes. Covers parameter names (`max_chars` → `max_sentence_chars`), local variables (`chunk`, `current_chunk`, `pre_chunks`, `last_chunk`), and method names (`_assembly_small_chunks`, `_sentenize_ssml_into_chunks`, `_build_valid_chunk`). Also covers the Russian text sentenizer and the `collect_chunks` test helper.

## Acceptance criteria

- [x] `text_sentenizer.py`: `max_chars` param → `max_sentence_chars`, `chunk`/`current_chunk`/`pre_chunks`/`last_chunk` → `sentence`/`current_sentence`/`pre_sentences`/`last_sentence`
- [x] `text_sentenizer.py`: `_assembly_small_chunks` → `_assembly_small_sentences`, `_sentenize_ssml_into_chunks` → `_sentenize_ssml_into_sentences`, `_build_valid_chunk` → `_build_valid_sentence`
- [x] `ru_text_sentenizer.py`: Same `max_chars` rename, `chunk_text` → `sentence_text`, `chunk` → `sentence`
- [x] `helpers.py`: `collect_chunks` → `collect_sentences`
- [x] Test files: method names (`test_short_text_returns_single_chunk` → `_single_sentence`, etc.), local vars (`chunks` → `sentences`, `chunk` → `sentence`), import references
- [x] All tests pass

## Blocked by

- None - can start immediately (independent of issue 2)
