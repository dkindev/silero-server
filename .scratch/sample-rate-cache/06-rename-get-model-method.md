---
title: "Rename get_model_path to get_model and return sample_rates"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Rename `get_model_path(language, model_name)` → `get_model(language, model_name)` returning `tuple[str, list[int]]`. Extract `sample_rate` from `models.yml` at path `tts_models[language][model_name]["latest"]["sample_rate"]`, returning `[]` if missing.

## Acceptance criteria

- [x] Method renamed to `get_model` in provider.py
- [x] Returns tuple(path: str, sample_rates: list[int])
- [x] Reads sample_rate from models.yml (tts_models -> language -> model_name -> latest -> sample_rate)
- [x] Returns [] if sample_rate not present in models.yml

## Blocked by

None - can start immediately