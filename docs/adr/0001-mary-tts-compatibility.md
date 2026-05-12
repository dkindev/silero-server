# ADR-0001: Mary-TTS Compatible API Surface

## Status

Accepted

## Context

The project wraps the Silero TTS engine with a REST API. We needed to decide on the public API contract — specifically whether to design a custom API or adopt an existing convention.

Two primary options were evaluated:

1. **Custom REST API** — e.g., `POST /api/v1/speak` with `{text, voice, language}` JSON. Clean slate, minimal surface area, fully tailored to Silero's capabilities.

2. **Mary-TTS compatible API** — e.g., `/process`, `/voices`, `/locales` with Mary-TTS parameter names (`INPUT_TEXT`, `LOCALE`, `VOICE`, `INPUT_TYPE`, `OUTPUT_TYPE`). Established convention used by TTS clients (MaryTTS, Coqui, Myrtle).

## Decision

We adopt the **Mary-TTS compatible API surface**.

## Reasons

**Mary-TTS compatibility is a hard requirement.** The project README explicitly commits to "Mary-TTS compatible REST API." Clients (web, mobile, desktop) targeting Mary-TTS servers can switch to this server with minimal code changes.

**Ecosystem compatibility.** Multiple TTS tools, sample clients, and integration guides reference Mary-TTS conventions. Adopting the same API surface lowers the barrier to adoption — no custom client library needed.

**Trade-off: Silero features vs. Mary-TTS coverage.** Silero does not support SSML fully, phoneme output, or prosody control. We handle this by:
- Accepting SSML input but stripping tags and processing text content (not rejecting it).
- Rejecting `PHONEMES`/`TOKENS` `OUTPUT_TYPE` with **406 Not Acceptable** — the server is honest about what it can and cannot do.
- Normalizing Silero's internal concepts (short language codes, speaker names) to Mary-TTS format (locales, voice names) at the API boundary.

**Trade-off: API verbosity.** Mary-TTS parameters use uppercase with underscores (`INPUT_TEXT`, `LOCALE`). This is less idiomatic for modern REST APIs but is the established convention for this space.

## Consequences

- **Positive:** Clients familiar with Mary-TTS can use this server immediately. Reduces client-side documentation burden.
- **Negative:** API surface includes concepts (SSML, PHONEMES, TOKENS, RAWMARYXML) that Silero doesn't support. We must handle these gracefully with 400/406 responses.
- **Negative:** Locale format normalization adds a translation layer between the API and Silero's internals.

## Alternatives Considered

| Alternative | Reason for Rejection |
|---|---|
| Custom JSON API (`/speak`) | Requires custom client libraries; no ecosystem compatibility |
| gRPC API | More efficient but less accessible to web/mobile clients |
| Streaming API (WebSocket) | Silero doesn't support streaming; adds complexity for minimal benefit |
| MaryTTS protocol (AMQP, etc.) | Overkill for HTTP-based clients; adds infrastructure dependencies |