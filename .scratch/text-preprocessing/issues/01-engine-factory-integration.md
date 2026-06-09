---
id: 1
title: "Text preprocessing — engine factory integration + TTS_MAX_CHUNK_CHARS"
labels:
  - ready-for-agent
created: 2026-06-09
---

## What to build

Wire the `TextPreprocessor` base class into the Silero TTS engine using a factory callable pattern, and add the `TTS_MAX_CHUNK_CHARS` environment variable.

### Engine changes

Replace the `text_preprocessors: dict[str, TextPreprocessor]` parameter in `SileroTTSEngine.__init__` with a `text_preprocessor_factory: Callable[[str], TextPreprocessor]` parameter.

In `process()`, call `text_preprocessor = self._text_preprocessor_factory(locale)` to obtain a preprocessor for the request's locale. If the factory returns a preprocessor, use `process_text()` (for `INPUT_TYPE=TEXT`) or `process_ssml()` (for `INPUT_TYPE=SSML`) with `max_chunk_chars` and `cached.model.symbols` as arguments. If no preprocessor is returned (factory returns `None`), fall back to treating the entire text as one chunk.

The factory signature: `Callable[[str], TextPreprocessor]` — locale string in, preprocessor instance out.

### Factory in deps.py

Define a `_TEXT_PREPROCESSOR_BUILDERS: dict[str, Callable[[], TextPreprocessor]]` mapping locale keys to zero-argument callables that return a preprocessor instance. Define a `build_text_preprocessor(locale: str) -> TextPreprocessor` function that looks up the locale in the dict and calls the builder, falling back to `TextPreprocessor()` if no builder is registered.

Initially only the fallback `TextPreprocessor()` is registered. No locale-specific preprocessors yet — that comes in the follow-up slice.

### TTS_MAX_CHUNK_CHARS env var

Add `TTS_MAX_CHUNK_CHARS: int = 140` to the Pydantic `Settings` class (validated ≥ 1). Wire it through `TTSConfig` (already has `max_chunk_chars` field) and `deps.py` so the engine receives it.

### Docs

- `CONTEXT.md`: add `TTS_MAX_CHUNK_CHARS` to the configuration table, add a TextPreprocessor section describing the factory pattern
- `README.md`: add `TTS_MAX_CHUNK_CHARS` to the env vars table
- `.env.example`: add `TTS_MAX_CHUNK_CHARS=140`

### Tests

- Unit tests for `TextPreprocessor.process_text` at sentence, punctuation, word, and hard-char split levels
- Unit tests for `TextPreprocessor.process_ssml` with valid XML, invalid XML fallback, and edge cases
- Set `mock_model.symbols = "abcdefghijklmnopqrstuvwxyz "` on all existing engine test mocks so the new `_normalize_text` regex doesn't break

## Acceptance criteria

- [x] `SileroTTSEngine.__init__` accepts a `Callable[[str], TextPreprocessor]` instead of `dict[str, TextPreprocessor]`
- [x] `process()` calls the factory to obtain a preprocessor per locale, and falls back to unchunked text when factory returns `None`
- [x] `build_text_preprocessor(locale)` factory function exists in `deps.py` with dict-based lookup and `TextPreprocessor()` fallback
- [x] `TTS_MAX_CHUNK_CHARS` env var controls chunk size (default 140), validated ≥ 1
- [x] All existing tests pass with `mock_model.symbols` set
- [x] Unit tests cover `TextPreprocessor.process_text` and `process_ssml`
- [x] `CONTEXT.md`, `README.md`, `.env.example` document `TTS_MAX_CHUNK_CHARS`

## Blocked by

None - can start immediately
