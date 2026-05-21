---
title: "Move global_exception_handler to handlers.py"
labels:
  - ready-for-agent
created: 2026-05-21
resolved: 2026-05-21
---

## What to build

Move `global_exception_handler` from `src/main.py` into a new `src/handlers.py` module. The function body stays identical — no behavior change.

## Acceptance criteria

- [x] `src/handlers.py` exists with `global_exception_handler` defined (identical body, same imports)
- [x] `src/main.py` imports `global_exception_handler` from `src.handlers` instead of defining it
- [x] `src/main.py` no longer imports `JSONResponse` (only used in the handler)
- [x] `tests/test_routers.py` imports `global_exception_handler` from `src.handlers`
- [x] `pytest` passes — pre-existing failure: handler returns 500 always, but tests expect it to read exception's `status_code`. Unrelated to the move.

## Blocked by

None — can start immediately
