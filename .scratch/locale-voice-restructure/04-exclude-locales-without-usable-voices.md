---
title: "Exclude locales with no usable voices from supported set"
labels:
  - ready-for-agent
created: 2026-06-11
---

## Parent

- /workspaces/python/.scratch/locale-voice-restructure/01-dataclass-storage-endpoints.md

## What to build

After the dataclass/storage restructure (issue 01), `_filter_enabled` preserves a quirk: locales with **zero voices** in the YAML config are still included in the supported set, while locales whose voices all reference disabled models are excluded. This is inconsistent.

Make the rule symmetric: **a locale is included only when at least one of its voices references an enabled model**. Locales with no voices, or whose voices all reference disabled or undefined models, are excluded.

This is a narrow change to `_filter_enabled` only — all public method signatures, endpoint responses, and the internal `_locales` dict structure stay the same.

The three-layer verification path:
1. **Config loading** — `_filter_enabled` no longer has the "locale without voices → include" branch
2. **Storage** — `get_locales()` and `has_locale()` reflect the filtered set
3. **API** — `GET /locales` omits such locales; `GET /process?LOCALE=xxx` returns 400

### Specific changes

**`_filter_enabled` (in storage class):**
- Remove the `locales_with_voices` intermediate set (no longer needed)
- Remove the `if locale.name not in locales_with_voices: append` branch
- Simplify to: a locale is kept iff `locale.name in locales_with_enabled_voices`

**Test update:**
- `test_get_locales_returns_locale_objects` creates a config with locales and zero voices → must be updated to expect 0 locales returned (or replaced with a test showing a locale-with-voices-kept scenario)

**CONTEXT.md:**
- Replace line 62 with the symmetric rule (already addressed separately in issue 02's scope, but ensure this issue's update takes precedence if both touch the same line)

## Acceptance criteria

- [x] `_filter_enabled` excludes locales with zero voices from `filtered_locales`
- [x] `_filter_enabled` continues to exclude locales whose voices all reference disabled/undefined models
- [x] `_filter_enabled` continues to include locales that have at least one voice on an enabled model
- [x] `get_locales()` and `has_locale()` reflect the filtered set
- [x] The `locales_with_voices` intermediate variable is removed
- [x] The affected test (`test_get_locales_returns_locale_objects`) is updated to match the new behavior
- [x] All existing tests pass

## Blocked by

- /workspaces/python/.scratch/locale-voice-restructure/01-dataclass-storage-endpoints.md
