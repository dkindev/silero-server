---
title: "Fix get_supported_text_formats return type and assertions"
labels:
  - ready-for-agent
created: 2026-06-22
---

## What to build

`get_supported_text_formats` returns `list[TextFormat]` but one of its tests expects a `tuple`. Two tests also assert membership using string literals `"TEXT"`/`"SSML"` against a container of `TextFormat` enum members, which never matches.

Change the method to return `tuple(TextFormat)` and update the two test assertions accordingly.

## Acceptance criteria

- [x] `test_get_input_types_returns_tuple` passes
- [x] `test_get_input_types_includes_text_and_ssml` passes
- [x] No other tests are broken

## Blocked by

None — can start immediately.
