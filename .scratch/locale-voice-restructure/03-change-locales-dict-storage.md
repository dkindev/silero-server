---
title: "Change _locales value type from list[VoiceConfig] to dict[str, VoiceConfig]"
labels:
  - ready-for-agent
created: 2026-06-11
---

## Parent

- /workspaces/python/.scratch/locale-voice-restructure/01-dataclass-storage-endpoints.md

## What to build

Change the internal `_locales` storage in `SileroTTSYamlConfigStorage` from `dict[str, tuple[Locale, list[VoiceConfig]]]` to `dict[str, tuple[Locale, dict[str, VoiceConfig]]]` keyed by `voice_name`. This converts O(n) list scans to O(1) dict lookups in `has_voice` and `get_voice_config`.

All public method signatures remain identical. Decisions made during design review:

- **Motivation:** Performance (dict lookup vs list scan)
- **Deduplication:** `voice_name` is unique per locale; dict enforces naturally
- **Error handling:** Bare `KeyError` from dict (no custom message)
- **`has_voice`** delegates to `get_voice_config` and catches `KeyError` -> `False`
- **No new public accessors**

## Acceptance criteria

- [x] `_build_locales_dict` produces `dict[str, tuple[Locale, dict[str, VoiceConfig]]]`
- [x] `get_voice_config` returns `voices[voice_name]` directly (bare KeyError on miss)
- [x] `get_voices` uses `voices.values()` to flatten
- [x] `has_voice` delegates to `get_voice_config`, returns `False` on KeyError
- [x] All existing tests pass unchanged

## Blocked by

- /workspaces/python/.scratch/locale-voice-restructure/01-dataclass-storage-endpoints.md
- /workspaces/python/.scratch/locale-voice-restructure/02-update-core-concept-docs.md (for CONTEXT.md changes)
