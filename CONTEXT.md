# Silero TTS Server — Domain Context

A simple, robust, and performant **Wyoming protocol TTS server** that wraps the
**Silero TTS** engine. Provides text-to-speech generation over TCP using the
Wyoming protocol, enabling integration with Home Assistant and other Wyoming
clients.

## Language

**TTS Engine**:
The core component that synthesizes speech from text input. Wraps Silero TTS
models and produces raw PCM audio output.
_Avoid_: Speech generator, voice synthesizer

**Model**:
A named, language-specific Silero TTS model entry in the YAML config. Models can
be enabled, disabled, or pre-warmed at startup. Each model supports one or more
speakers.
_Avoid_: Neural network, PyTorch model

**Speaker**:
A named voice profile within a model (e.g., `aidar`, `eugene`, `baya`). Speakers
are model-specific — the same speaker name may refer to different voices across
different models.
_Avoid_: Voice (when meaning a speaker profile)

**Locale**:
A language-region string (e.g., `ru_RU`, `en_US`) that groups voices. The
language code is extracted from the locale for the Wyoming protocol. A locale is
available only when at least one voice backed by an enabled model carries it.
_Avoid_: Language (when referring to the locale as a whole)

**Voice**:
A named, locale-specific voice backed by a model speaker. Each voice has a
unique ID in the format `{locale}-{model}-{name}` (e.g.,
`ru_RU-v5_5_ru-aidar`), which identifies it in the Wyoming protocol. Each voice
belongs to exactly one locale and references one model.
_Avoid_: Speaker (when meaning a named voice)

**Chunk**:
A segment of text split from the input to stay within model length limits.
Multiple chunks are synthesized separately and streamed as a single audio
response.
_Avoid_: Segment, fragment

**Wyoming**:
A TCP-based protocol for Home Assistant integration. The server advertises
supported locales and voices via Wyoming Info events, accepts synthesis
requests, and streams audio back as Wyoming audio events.
_Avoid_: REST API, HTTP

## Relationships

- A **Model** supports one or more **Speakers**
- A **Speaker** belongs to exactly one **Model**
- A **Locale** has one or more **Voices**
- A **Voice** belongs to exactly one **Locale**, references exactly one
  **Model**, and maps to exactly one **Speaker**
- The **TTS Engine** loads a **Model**, selects a **Speaker**, splits text into
  **Chunks**, and outputs PCM audio
- The server advertises supported **Locales** and **Voices** over the **Wyoming**
  protocol

## Example dialogue

> **Dev:** "If I configure a **Voice** `henry` under locale `en_US` backed by
> model `v3_en`, does the **TTS Engine** load the model immediately?"
> **Domain expert:** "No — the **Model** is only loaded when the first synthesis
> request arrives, unless its `warmup` is set to `true`."
> **Dev:** "And if the text exceeds the **Chunk** limit, does each chunk produce
> separate audio?"
> **Domain expert:** "Each **Chunk** produces PCM audio. The **Wyoming** handler
> streams them as a single AudioStart/AudioChunk/AudioStop sequence to the
> client."

## Flagged ambiguities

- "Mary-TTS compatible REST API" was used to describe this project —
  resolved: this is a **Wyoming protocol server**, not an HTTP REST API
- "Model" was used to mean both a config entry and the loaded neural network —
  resolved: **Model** is a configuration concept
