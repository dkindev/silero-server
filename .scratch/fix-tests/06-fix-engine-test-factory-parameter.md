---
title: "Fix engine test factory parameter (text_preprocessor_factory → text_sentenizer_factory)"
labels:
  - ready-for-agent
created: 2026-06-25
---

## What to build

`SileroTTSEngine.__init__` now takes `text_sentenizer_factory: Callable[[str, TextFormat], TextSentenizer]` but `tests/test_engine.py` still passes the old keyword `text_preprocessor_factory=lambda _: TextNormalizer()`. This fails because:

1. The parameter name changed
2. `TextNormalizer` is an ABC — can't be instantiated
3. The factory signature changed from `Callable[[str], TextPreprocessor]` to `Callable[[str, TextFormat], TextSentenizer]`

### Changes (22 occurrences across `tests/test_engine.py`)

- Change `text_preprocessor_factory=` → `text_sentenizer_factory=`
- Change `lambda _: TextNormalizer()` → `lambda locale, fmt: SimpleTextSentenizer()`
- Update import from `TextNormalizer` to `SimpleTextSentenizer`

## Acceptance criteria

- [x] All 22 tests in `test_engine.py` pass
- [x] No other tests are broken

## Blocked by

- [#4](04-fix-sentenizer-return-types.md) — `SimpleTextSentenizer.text_to_sentences` must return a proper `list[str]` or the engine's chunk iteration breaks
