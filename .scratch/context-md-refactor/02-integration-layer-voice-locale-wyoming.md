---
title: "Slice 2: Integration layer — Locale, Voice, Wyoming"
labels:
  - ready-for-agent
created: 2026-06-18
---

## What to build

Add the remaining three domain terms (Locale, Voice, Wyoming) to CONTEXT.md after Slice 1's core terms are in place. Expand the Relationships section to cover how voices are grouped under locales, backed by models, and advertised over the Wyoming protocol. Update the Example dialogue to include voice/locale/wyoming questions.

Add these definitions:

- **Locale**: A language-region string (e.g., `ru_RU`, `en_US`) that groups voices. The language code is extracted from the locale for the Wyoming protocol. A locale is available only when at least one voice backed by an enabled model carries it. *Avoid*: Language (when referring to the locale as a whole)
- **Voice**: A named, locale-specific voice backed by a model speaker. Each voice has a unique ID in the format `{locale}-{model}-{name}` (e.g., `ru_RU-v5_5_ru-aidar`), which identifies it in the Wyoming protocol. Each voice belongs to exactly one locale and references one model. *Avoid*: Speaker (when meaning a named voice)
- **Wyoming**: A TCP-based protocol for Home Assistant integration. The server advertises supported locales and voices via Wyoming Info events, accepts synthesis requests, and streams audio back as Wyoming audio events. *Avoid*: REST API, HTTP

Extend **Relationships**:
- A Locale has one or more Voices
- A Voice belongs to exactly one Locale, references exactly one Model, and maps to exactly one Speaker
- The server advertises supported Locales and Voices over the Wyoming protocol

Extend **Example dialogue** with Q&A about voice configuration and Wyoming discovery.

## Acceptance criteria

- [x] Locale, Voice, Wyoming are defined with `_Avoid_` aliases
- [x] Relationships cover Locale→Voice, Voice→Locale/Model/Speaker, Wyoming→Locales/Voices
- [x] Example dialogue includes a device that asks about voice configuration and protocol discovery
- [x] All new terms reference existing terms from Slice 1 (Model, Speaker, TTS Engine) correctly

## Blocked by

- Slice 1: Project identity fix + core engine terms
