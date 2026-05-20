---
title: "Remove sample_rates from Model dataclass and config loading"
labels:
  - ready-for-agent
created: 2026-05-20
---

## What to build

Remove `sample_rates` field from `Model` dataclass in `models.py` and remove the sample_rates loading logic in `load_config_model()`.

## Acceptance criteria

- [ ] Model dataclass no longer has sample_rates field
- [ ] load_config_model() no longer reads sample_rate/sample_rates from config

## Blocked by

.scratch/sample-rate-cache/07-engine-use-sample-rates-from-provider.md