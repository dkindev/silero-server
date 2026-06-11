---
title: "Modernize CI workflow"
labels:
  - ready-for-agent
created: 2026-06-11
---

## What to build

Update `.github/workflows/ci.yml` to add Python 3.14 to the build matrix and
replace `pip install -e ".[dev]"` with `uv sync --extra dev` for dependency
installation in both lint and test jobs.

## Acceptance criteria

- [ ] Python 3.14 added to the `strategy.matrix.python-version` list in both jobs
- [ ] `pip install` blocks replaced with `uv sync --extra dev` in both jobs
- [ ] CI run passes on all four Python versions (3.11, 3.12, 3.13, 3.14)

## Blocked by

None — can start immediately
