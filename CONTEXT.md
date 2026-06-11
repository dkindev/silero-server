# Silero TTS Server — Domain Context

## Project Overview

A simple, robust, and performant **Mary-TTS compatible HTTP API** that wraps the
**Silero TTS** engine. Provides text-to-speech generation over HTTP with minimal
latency and operational overhead.

## Core Concepts

### TTS Engine

The core component that synthesizes speech from text input. Wraps the underlying
Silero TTS neural network models and produces audio output. Supports two input
types (TEXT and SSML) and produces WAV audio.

### Model

A Silero neural network model for a specific language (e.g., Russian, English).
Models are downloaded per language and loaded into memory on demand. Each model
supports one or more speakers and one or more sample rates.

### Speaker

A named voice profile within a model (e.g., `aidar`, `eugene`, `baya`). Speakers
are model-specific — the same speaker name may refer to different voices across
different models.

### Sample Rate

Audio output frequency in Hz. The engine selects the best matching sample rate
from the model's supported rates relative to the configured target.

### Locale

A language-region identifier in Mary-TTS format (e.g., `ru_RU`, `en_US`).
Locales are exposed in the API and mapped to underlying model languages. A
locale is available only when it has at least one voice backed by an enabled
model.

### Voice

A named, locale-specific voice backed by a model speaker. Each voice belongs to
exactly one locale and references a model. A voice is available only when its
referenced model is enabled.

### Input Type

The format of input text: **TEXT** (plain text) or **SSML** (structured markup).

### Output Type

The format of output audio: **AUDIO** (WAV). Other output types are not
supported.

### Chunk

A segment of text split from the input to stay within model length limits.
Multiple chunks for a single input are synthesized separately and concatenated
into one audio output.
