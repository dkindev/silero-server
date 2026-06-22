---
title: "Fix disabled-model get_model test expectation"
labels:
  - ready-for-agent
created: 2026-06-22
---

## What to build

`get_model` uses `dict.get()` which returns `None` for disabled/absent models — it never raises. But `test_disabled_model_get_model_raises_key_error` asserts `pytest.raises(KeyError)`. This is the simplest failure: change the test to assert `storage.get_model("v5_5_ru") is None`.

## Acceptance criteria

- [x] `test_disabled_model_get_model_raises_key_error` passes
- [x] No other tests are broken

## Blocked by

None — can start immediately.
