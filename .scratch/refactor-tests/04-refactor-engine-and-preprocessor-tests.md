---
title: "Refactor engine and preprocessor tests"
labels:
  - ready-for-agent
created: 2026-06-19
---

## What to build

Refactor `test_engine.py` (1129 lines) to use the shared mock fixtures from `conftest.py`. This is the largest refactor — the file has ~14 blocks of repeated `unittest.mock.patch("src.tts.engine.torch.package.PackageImporter", ...)` boilerplate, each ~20 lines.

Also standardize `test_text_preprocessor.py` (71 lines) and `test_ru_text_preprocessor.py` (49 lines) to use module-level imports.

Changes:
- Replace inline mock patterns with conftest `mock_model` and `mock_importer` fixtures
- Replace repeated `TTSConfig(...)` construction with `default_tts_config` fixture (overriding only the fields that differ per test)
- Use `make_models_dir`, `make_voice`, `make_model`, `collect_chunks` from conftest
- Move late imports to module level across all three files
- No functional changes to test coverage

## Acceptance criteria

- [x] All imports are at module level (no `from src.tts.engine import ...` inside test bodies)
- [x] Inline `unittest.mock.patch("src.tts.engine.torch.package.PackageImporter", ...)` blocks are replaced with conftest fixtures
- [x] Inline `TTSConfig(...)` construction is replaced with `default_tts_config` fixture
- [x] `pytest tests/test_engine.py tests/test_text_preprocessor.py tests/test_ru_text_preprocessor.py` passes
- [x] Test coverage is identical (no tests removed)

## Blocked by

- `01-create-shared-test-infrastructure`
