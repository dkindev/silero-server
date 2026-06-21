---
title: "Derive locale language from locale name instead of reading from config.yml"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

The `SileroTTSYamlConfigStorage._load_config_model()` method currently reads a
`language:` key from each locale entry in `config.yml` (with a fallback to the
parent model's `language`). This is redundant — the locale name itself encodes
the language as `<language>_<REGION>` (e.g., `ru_RU` → `ru`, `en_US` → `en`).

Replace the YAML lookup with a derivation from the locale name:

`language = locale_name.split("_")[0]`

Scope of changes:

- **`src/tts/config_storage.py`** — one-line change in `_load_config_model()`
- **`config.yml`** — remove `language:` keys from all locale entries (they are
  now unused)
- **`tests/test_config_storage.py`** — remove `language:` from all 15 YAML
  fixture strings at the locale level
- **`tests/test_engine.py`** — remove `language:` from the 1 YAML fixture
  string; update `make_locale()` helper to drop `language="ru"` default
- **`tests/test_tts_models.py`** — no change needed; the 3 direct
  `Locale(name=..., language=...)` constructions test the raw dataclass, not
  the parser

The `Locale` dataclass is unchanged — it still has `name` and `language`
fields. `Model.language` (model-level YAML key) is also unchanged.

The `locale_data.get("language", model_data["language"])` expression at
`config_storage.py:65` becomes simply `locale_name.split("_")[0]`.

Edge cases handled:
- `"ru_RU"` → `"ru"` (standard form)
- `"en_US"` → `"en"` (standard form)
- `"ru"` (no region suffix) → `"ru"` (bare name, still works)

## Acceptance criteria

- [x] `Locale.language` is derived from `locale_name.split("_")[0]` instead of YAML lookup
- [x] `config.yml` locale entries no longer contain `language:` keys
- [x] `locale.language` continues to work everywhere (Wyoming info, engine, etc.)
- [x] All existing tests pass
- [x] Edge cases verified: `"ru_RU"`, `"en_US"`, and bare `"ru"` all produce correct language strings

## Blocked by

None — can start immediately
