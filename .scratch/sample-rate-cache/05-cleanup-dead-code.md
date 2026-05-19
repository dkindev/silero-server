---
title: "Clean up dead code"
labels:
  - ready-for-agent
created: 2026-05-19
---

## What to build

Remove the now-unused `self._model_semaphores` dict from `__init__` and update the type hint for `self._models` to reflect that it now stores `CachedModel` instances instead of raw models.

## Acceptance criteria

- [x] self._model_semaphores removed from __init__
- [x] self._models type hint updated to dict[str, CachedModel]
- [x] No other references to the removed dict exist

## Blocked by

- 04-update-process-method