---
title: "Production gunicorn setup"
labels:
  - needs-triage
created: 2026-05-19
---

## What to build

Add gunicorn for production server deployment.

- Add gunicorn to dependencies in pyproject.toml
- Update Dockerfile to use gunicorn instead of uvicorn
- Configure appropriate worker count

## Acceptance criteria

- [x] gunicorn in dependencies
- [x] Dockerfile runs gunicorn
- [x] App serves correctly via gunicorn

## Blocked by

05-post-process