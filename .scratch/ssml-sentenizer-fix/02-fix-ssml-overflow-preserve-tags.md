---
title: "Fix SSML text overflow to preserve tag structure in chunks"
labels:
  - ready-for-agent
created: 2026-07-01
---

## Parent

[01-clarify-max-chunk-chars-semantics.md](01-clarify-max-chunk-chars-semantics.md)

## What to build

When `_sentenize_ssml_into_chunks` encounters a text token that exceeds `max_chunk_chars` and the chunk has accumulated opening tags (like `<p>`), the current code:

1. Yields the opening tags alone as an empty chunk (`<p></p>` → stripped to empty)
2. Wraps each sub-sentence with only closing tags (missing opening tags)
3. Synthetically wraps `<speak>` around without the structural tags

The result is malformed chunks like `<speak></speak>`, `<speak>hello</p></speak>`, and `<speak></p></speak>`.

Fix: when text overflows, carry the currently-open structural tags forward into each sub-chunk as prefix tokens, then consume the trailing closing tags from the input stream that were already emitted by the sentenizer. Each emitted chunk is a self-contained, valid XML fragment with properly opened and closed structural tags.

## Acceptance criteria

- [x] `test_ssml_splits_long_text_and_reopens_tags` produces exactly 3 chunks matching the expected list: `["<speak><p>hello</p></speak>", "<speak><p>world foo</p></speak>", "<speak><p>bar baz</p></speak>"]`
- [x] `test_valid_ssml_preserves_structure` and `test_invalid_ssml_falls_back_to_text_split` still pass
- [x] All non-SSML sentenizer tests still pass
- [x] Nested tags (e.g. `<p><s>text</s></p>`) produce self-contained chunks when text overflows

## Blocked by

- [01-clarify-max-chunk-chars-semantics.md](01-clarify-max-chunk-chars-semantics.md) — the fix assumes `max_chunk_chars` limits text content only
