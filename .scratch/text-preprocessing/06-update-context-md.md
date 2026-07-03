---
id: 6
title: "Update CONTEXT.md with Text normalization term"
labels:
  - ready-for-agent
created: 2026-07-03
---

## What to build

Add **Text normalization** to `CONTEXT.md` glossary, update **Relationships** to show normalization follows text splitting, and add a flagged ambiguity.

### Changes

#### Language section — add term

```
**Text normalization**:
The preprocessing step applied to text before TTS synthesis that ensures clean input by stripping whitespace and removing characters unavailable in the active model.
_Avoid_: Preprocessing, text cleaning, normalization (alone)
```

#### Relationships — update engine line

Change:

```
- The **TTS Engine** loads a **Model**, selects a **Speaker**, splits text into
  **Chunks**, and outputs PCM audio
```

To:

```
- The **TTS Engine** loads a **Model**, selects a **Speaker**, splits text into
  **Chunks**, applies **Text normalization** to each chunk, and outputs PCM audio
```

#### Relationships — add new line

```
- **Text normalization** is applied to each **Chunk** after text splitting and before synthesis
```

#### Flagged ambiguities — add entry

```
- "normalizer" was used to mean both PlainTextNormalizer and OpenAiTextNormalizer — resolved: **Text normalization** is the abstract concept; specific implementations are implementation details
```

## Acceptance criteria

- [x] `CONTEXT.md` Language section includes **Text normalization** term
- [x] `CONTEXT.md` Relationships shows normalization after text splitting
- [x] `CONTEXT.md` Flagged ambiguities includes the normalizer/implementation entry
- [x] All existing terms remain unchanged

## Blocked by

None - can start immediately
