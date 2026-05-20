---
title: "Update engine to use sample_rates from provider"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Update `silero_tts_engine.py` to call `get_model` and use the returned sample_rates when calling `select_sample_rate()`.

## Acceptance criteria

- [ ] Engine calls `get_model(language, model_name)` instead of `get_model_path`
- [ ] Unpacks tuple: `local_path, sample_rates = self._provider.get_model(...)`
- [ ] Passes sample_rates from provider to `select_sample_rate()`

## Blocked by

.scratch/sample-rate-cache/06-rename-get-model-method.md