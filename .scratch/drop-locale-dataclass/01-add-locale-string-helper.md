---
title: "Add get_language_from_locale_string() helper"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Add a pure utility function `get_language_from_locale_string()` to `src/tts/models.py` that extracts the language code from a locale string (e.g., `"en_US"` → `"en"`, `"en-US"` → `"en"`, `"en.UTF-8"` → `"en"`).

The function splits by underscores, hyphens, or dots and returns the first segment. If the input is empty or yields no segments, it returns `None`.

Signature:
```python
def get_language_from_locale_string(locale_str: str) -> str | None:
```

Add a corresponding test class `TestGetLanguageFromLocaleString` in `tests/test_tts_models.py` covering:
- `en_US` → `"en"`
- `ru_RU` → `"ru"`
- `en-US` → `"en"`
- `en.UTF-8` → `"en"`
- Empty string `""` → `None`
- Single segment `"en"` → `"en"`

Pure addition — no callers, no deletions, no other files changed.

## Acceptance criteria

- [x] Function exists at `src.tts.models.get_language_from_locale_string`
- [x] Returns correct language for underscore format (`en_US`, `ru_RU`)
- [x] Returns correct language for hyphen format (`en-US`)
- [x] Returns correct language for dot format (`en.UTF-8`)
- [x] Returns `None` for empty string input
- [x] All new tests pass (`pytest tests/test_tts_models.py -k TestGetLanguageFromLocaleString`)

## Blocked by

None — can start immediately
