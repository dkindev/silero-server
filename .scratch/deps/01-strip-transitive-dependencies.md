---
title: "Strip transitive dependencies from pyproject.toml"
labels:
  - completed
created: 2026-06-22
---

## What to build

Remove 11 transitive-only dependencies from `[project.dependencies]` in `pyproject.toml` that are never imported directly by the project code. These are pinned transitive dependencies of PyTorch (and its ecosystem) that `uv`/`pip` resolve automatically — they don't belong in the project's own dependency list.

### Remove these:
- `antlr4-python3-runtime`
- `filelock`
- `fsspec`
- `jinja2`
- `markupsafe`
- `mpmath`
- `networkx`
- `scipy`
- `setuptools`
- `sympy`
- `typing-extensions`

### Keep these (9 direct deps):
- `pydantic>=2.0.0`
- `pydantic-settings>=2.0.0`
- `torch==2.12.1`
- `numpy==2.4.6`
- `pyyaml==6.0.3`
- `loguru>=0.7.3`
- `razdel>=0.5.0`
- `wyoming>=1.9.0`
- `zeroconf>=0.149.16`

## Acceptance criteria

- [x] The 11 transitive deps are removed from `[project.dependencies]` in `pyproject.toml`
- [x] `uv lock` succeeds without errors
- [x] Full test suite passes (`uv run pytest`)
- [x] `uv sync` installs cleanly and `import torch`, `import wyoming`, etc. still work

## Blocked by

None — can start immediately
