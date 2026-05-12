---
title: "Update minimum Python version to 3.11"
labels:
  - ready-for-agent
created: 2026-05-09
---

## What to build

Update minimum Python version from 3.10 to 3.11 across all configuration files.

## Acceptance criteria

- [x] `pyproject.toml` - `requires-python = ">=3.11"`
- [x] `pyproject.toml` - ruff `target-version = "py311"`
- [x] `pyproject.toml` - mypy `python_version = "3.11"`
- [x] `.github/workflows/ci.yml` - remove `3.10` from test matrix

## Blocked by

None