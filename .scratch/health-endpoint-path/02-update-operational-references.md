---
title: "Update operational references to /health"
labels:
  - ready-for-agent
closed: 2026-06-04
created: 2026-06-04
---

## What to build

Update all non-code references from `/api/v1/health` to `/health` after the route has been moved.

Changes required:
- Docker HEALTHCHECK URL in `Dockerfile`
- Health endpoint documentation in `CONTEXT.md` (path + versioning convention line)
- Endpoint reference in `README.md`

## Acceptance criteria

- [x] Docker HEALTHCHECK hits `http://localhost:8000/health`
- [x] `CONTEXT.md` lists endpoint as `GET /health` with no `/api/v1` prefix
- [x] `CONTEXT.md` versioning convention no longer claims "All routes under /api/v1/" — replaced with "Not versioned at the URL path level. Mary TTS compatibility requires root-level paths."
- [x] `README.md` health endpoint reference uses `/health`
- [x] `grep -r '/api/v1/health' src/ Dockerfile CONTEXT.md README.md` returns no matches

## Blocked by

- Move health endpoint to root path (slice 1)
