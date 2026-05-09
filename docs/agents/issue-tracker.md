# Issue Tracker

**Type:** Local markdown

## Overview

Issues are tracked as markdown files under `.scratch/` in the repository root.

## Workflow

- Create issues as `.scratch/<feature>/<issue-title>.md`
- Use frontmatter for metadata:
  ```yaml
  ---
  title: "Issue title"
  labels:
    - needs-triage
  created: 2026-05-09
  ---
  ```
- Update the `labels` array to reflect issue state transitions

## Skills that use this

- `to-issues` — creates new issues from plans/specs
- `triage` — moves issues through the state machine
- `to-prd` — creates PRDs as issues