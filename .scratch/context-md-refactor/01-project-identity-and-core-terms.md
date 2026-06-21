---
title: "Slice 1: Project identity fix + core engine terms"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Fix the project identity across all documentation so it consistently says "Wyoming protocol server" instead of "Mary-TTS compatible REST API". Then write the CONTEXT.md overview and the first three domain terms (TTS Engine, Model, Speaker) with their relationships, a matching example dialogue, and the Model ambiguity flag.

Specifically:

1. **AGENTS.md** — change the first line from `"A simple, robust, and performant Mary-TTS compatible REST API that wraps the Silero TTS engine..."` to `"A simple, robust, and performant Wyoming protocol TTS server that wraps the Silero TTS engine..."`

2. **README.md** — change the first sentence from `"A simple, robust, and performant Mary-TTS compatible HTTP API..."` to `"A simple, robust, and performant Wyoming protocol TTS server..."`

3. **CONTEXT.md** — replace the entire file with the new structure:
   - **Overview**: "A simple, robust, and performant Wyoming protocol TTS server that wraps the Silero TTS engine. Provides text-to-speech generation over TCP using the Wyoming protocol, enabling integration with Home Assistant and other Wyoming clients."
   - **TTS Engine**: The core component that synthesizes speech from text input. Wraps Silero TTS models and produces raw PCM audio output. *Avoid*: Speech generator, voice synthesizer
   - **Model**: A named, language-specific Silero TTS model entry in the YAML config. Models can be enabled, disabled, or pre-warmed at startup. Each model supports one or more speakers. *Avoid*: Neural network, PyTorch model
   - **Speaker**: A named voice profile within a model (e.g., `aidar`, `eugene`, `baya`). Speakers are model-specific — the same speaker name may refer to different voices across different models. *Avoid*: Voice (when meaning a speaker profile)
   - **Relationships**: Model → Speaker (one-to-many), Speaker → Model (many-to-one)
   - **Example dialogue** covering model loading (lazy vs warm) and speaker selection
   - **Flagged ambiguities**: "Model" was used to mean both a config entry and the loaded neural network — resolved: Model is a configuration concept

## Acceptance criteria

- [x] AGENTS.md no longer mentions "Mary-TTS compatible REST API"
- [x] README.md no longer mentions "Mary-TTS compatible HTTP API"
- [x] CONTEXT.md has the corrected overview
- [x] TTS Engine, Model, Speaker are defined with `_Avoid_` aliases
- [x] Relationships section shows Model–Speaker cardinality
- [x] Example dialogue demonstrates model loading behavior
- [x] Flagged ambiguities flags the Model concept muddle

## Blocked by

None — can start immediately
