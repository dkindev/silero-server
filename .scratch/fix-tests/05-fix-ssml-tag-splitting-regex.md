---
title: "Fix SSML tag splitting regex — use capturing group to preserve XML tags"
labels:
  - ready-for-agent
created: 2026-06-25
---

## What to build

`SsmlSentenizer._sentenize_ssml_into_chunks` uses `TAGS_RE.split(ssml_text)` with a non-capturing regex `r"<[^>]+>"`. This discards all XML tags, so the tag-tracking stack is never populated and the `if token.startswith("<")` branch is dead code. The SSML sentenizer then produces chunks that are missing their inner tags.

### Changes

In `src/tts/preprocessing/text_sentenizer.py`:

- Add a new regex with a capturing group: `TAGS_SPLIT_RE = re.compile(r"(<[^>]+>)")`
- In `_sentenize_ssml_into_chunks`, change `TAGS_RE.split(ssml_text)` → `TAGS_SPLIT_RE.split(ssml_text)`
- Keep the existing `TAGS_RE` for the `.sub()` calls (they don't need the capture group)

This makes the tag-tracking stack work correctly: each XML tag becomes a separate token in the list, gets parsed by `process_xml_tag`, and gets tracked/restored when chunks are split.

### Impact

- `<speak><p>hello world foo bar baz</p></speak>` with `max_chunk_chars=10` correctly splits into:
  - `<speak><p>hello</p></speak>`
  - `<speak><p>world foo</p></speak>`
  - `<speak><p>bar baz</p></speak>`
- Invalid SSML still falls back to plain text sentenization
- All existing `TAGS_RE.sub()` calls (fallback paths, chunk cleanup) are unaffected

## Acceptance criteria

- [x] SSML with short text returns a single properly-wrapped chunk (e.g. `<speak>hello world</speak>` preserved)
- [x] SSML with long text inside tags correctly splits and reopens tags per chunk
- [x] Invalid SSML falls back to plain text sentenization wrapped in `<speak>...</speak>`
- [x] No other `TAGS_RE` usage is broken (the fallback and cleanup uses of `.sub()` are unchanged)

## Blocked by

- [#4](04-fix-sentenizer-return-types.md) — Return type fixes must be merged first (return type issues would mask or confuse the SSML tag behavior)
