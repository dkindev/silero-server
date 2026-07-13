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
A named, language-specific Silero TTS model. Models can be enabled, disabled, 
or pre-warmed at startup. Each model supports one or more speakers.
_Avoid_: Neural network, PyTorch model

**Speaker**:
A named voice profile within a model (e.g., `aidar`, `eugene`, `baya`). Speakers
are model-specific — the same speaker name may refer to different voices across
different models.
_Avoid_: Voice (when meaning a speaker profile)

**Locale**:
A language-region string (e.g., `ru_RU`, `en_US`) that groups voices. A locale is
available only when at least one voice backed by an enabled model carries it.
_Avoid_: Language (when referring to the locale as a whole)

**Voice**:
A named, locale-specific voice backed by a model speaker. Each voice has a
unique ID, belongs to exactly one locale and references one model.
_Avoid_: Speaker (when meaning a named voice)

**Sentence**:
A segment of text split from the input to stay within model length limits.
Multiple Sentences are synthesized separately and streamed as a single audio
response.
_Avoid_: Segment, fragment

**Chunk**:
Raw PCM audio bytes produced by the **TTS Engine** for streaming over the
Wyoming protocol.
_Avoid_: Audio packet, byte fragment, PCM segment

**Text normalization**:
The preprocessing step applied to text before TTS synthesis that ensures clean input by stripping whitespace and removing characters unavailable in the active model.
_Avoid_: Preprocessing, text cleaning, normalization (alone)

**VoiceNormalization**:
A per-voice, per-text-format override of normalization settings. Links a voice to a specific normalization type (simple or LLM), optionally referencing a reusable prompt. When present, it overrides the server-wide default for that voice and text format combination.
_Avoid_: Normalization override, voice normalisation config

**Promt**:
A reusable LLM prompt definition that specifies the instruction text and which LLM model to use for LLM-based text normalization. Note: "promt" is an intentional misspelling carried over from the original codebase — do not "correct" it to "prompt" in code or domain language.
_Avoid_: Prompt (in code context), LLM instruction

## Relationships

- A **Model** supports one or more **Speakers**
- A **Speaker** belongs to exactly one **Model**
- A **Locale** has one or more **Voices**
- A **Voice** belongs to exactly one **Locale**, references exactly one
  **Model**, and maps to exactly one **Speaker**
- The **TTS Engine** loads a **Model**, selects a **Speaker**, splits text into
  **Sentences**, applies **Text normalization** to each **Sentence**, synthesizes
  each **Sentence** into one or more **Chunks**, and streams the **Chunks** over
  the Wyoming protocol
- The server advertises supported **Voices** over the **Wyoming**
  protocol
- A **Voice** has zero or more **VoiceNormalizations** (per text format overrides)
- A **Promt** is referenced by zero or more **VoiceNormalizations** (shared LLM prompt definitions)

## Example dialogue

> **Dev:** "If I configure a **Voice** `henry` under locale `en_US` backed by
> model `v3_en`, does the **TTS Engine** load the model immediately?"
> **Domain expert:** "No — the **Model** is only loaded when the first synthesis
> request arrives, unless its `warmup` is set to `true`."
> **Dev:** "And if the text exceeds the **Sentence** limit, does each sentence
> produce separate audio?"
> **Domain expert:** "Each **Sentence** is synthesized into **Chunks** of PCM
> audio. The server streams all the **Chunks** back as one continuous audio
> response over the Wyoming protocol."
> **Dev:** "How does LLM-based **Text normalization** work for a specific voice?"
> **Domain expert:** "You create a **VoiceNormalization** linking the voice to
> `NormalizationType.LLM`, and optionally attach a **Promt** that tells the LLM
> which model and instruction to use. If no **VoiceNormalization** exists for
> that voice and text format, the server-wide default applies."

## Flagged ambiguities

- "Model" was used to mean both a config entry and the loaded neural network —
  resolved: **Model** is a configuration concept
- "Promt" is a misspelling of "prompt" — this is intentional, carried over from
  the original codebase. Do not correct it in code or domain language.