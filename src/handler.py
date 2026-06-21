import re

from loguru import logger
from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.error import Error
from wyoming.event import Event
from wyoming.info import Attribution, Describe, Info, TtsProgram, TtsVoice
from wyoming.server import AsyncEventHandler
from wyoming.tts import (
    Synthesize,
    SynthesizeChunk,
    SynthesizeStart,
    SynthesizeStop,
    SynthesizeStopped,
)

from src import __metadata__, __project_urls__
from src.tts.engine import SileroTTSEngine


def _get_language_from_locale_string(locale_str: str) -> str | None:
    if not locale_str:
        return None
    parts = re.split(r"[_.-]", locale_str)
    return parts[0] if parts else None


def _create_wyoming_info(engine: SileroTTSEngine, streaming: bool) -> Info:
    storage = engine.get_storage()
    voices = []
    for voice in storage.get_voices():
        voices.append(
            TtsVoice(
                name=voice.id,
                description=voice.name,
                attribution=Attribution(
                    name="silero",
                    url="https://github.com/snakers4/silero-models",
                ),
                installed=True,
                languages=[_get_language_from_locale_string(voice.locale)],
                version=None,
            )
        )

    voices.sort(key=lambda v: v.name)

    return Info(
        tts=[
            TtsProgram(
                name=__metadata__["name"],
                description=__metadata__["summary"],
                attribution=Attribution(
                    name=__metadata__["name"],
                    url=__project_urls__["Homepage"],
                ),
                installed=True,
                voices=voices,
                supports_synthesize_streaming=streaming,
                version=__metadata__["version"],
            )
        ],
    )


class SileroWyomingHandler(AsyncEventHandler):
    def __init__(
        self,
        engine: SileroTTSEngine,
        supports_synthesize_streaming: bool,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.engine = engine
        self.supports_synthesize_streaming = supports_synthesize_streaming
        self.is_streaming: bool | None = None
        self._synthesize: Synthesize | None = None

    async def handle_event(self, event: Event) -> bool:
        try:
            logger.info("Handle '{event_type}'", event_type=event.type)
            logger.debug("Event: {event}", event=event)

            if Describe.is_type(event.type):
                return await self._handle_describe(event)

            if Synthesize.is_type(event.type):
                if self.is_streaming:
                    # Ignore since this is only sent for compatibility reasons.
                    # For streaming, we expect:
                    # [synthesize-start] -> [synthesize-chunk]+ -> [synthesize]? -> [synthesize-stop]
                    return True

                # Sent outside a stream, so we must process it
                return await self._handle_synthesize(event)

            if not self.supports_synthesize_streaming:
                # Streaming is not enabled
                return True

            if SynthesizeStart.is_type(event.type):
                return await self._handle_synthesize_start(event)

            if SynthesizeChunk.is_type(event.type):
                return await self._handle_synthesize_chunk(event)

            if SynthesizeStop.is_type(event.type):
                return await self._handle_synthesize_stop(event)
        except Exception as err:
            logger.exception(err)
            await self.write_event(Error(text=str(err), code=err.__class__.__name__).event())
            return False

        return True

    async def _handle_synthesize(self, event: Event) -> bool:
        synthesize = Synthesize.from_event(event)
        state = await self._synthesize_pcm_chunks(synthesize=synthesize)
        return state

    async def _handle_synthesize_start(self, event: Event) -> bool:
        stream_start = SynthesizeStart.from_event(event)
        self.is_streaming = True
        self._synthesize = Synthesize(text="", voice=stream_start.voice)
        logger.debug("Text stream started: voice='{voice}'", voice=stream_start.voice)
        return True

    async def _handle_synthesize_chunk(self, event: Event) -> bool:
        assert self._synthesize is not None
        stream_chunk = SynthesizeChunk.from_event(event)
        self._synthesize.text = stream_chunk.text
        state = await self._synthesize_pcm_chunks(self._synthesize)
        logger.debug("Text stream processed.")
        return state

    async def _handle_synthesize_stop(self, event: Event) -> bool:
        assert self._synthesize is not None
        await self.write_event(SynthesizeStopped().event())
        logger.debug("Text stream stopped")
        return True

    async def _handle_describe(self, event: Event) -> bool:
        wyoming_info_event = _create_wyoming_info(
            self.engine, self.supports_synthesize_streaming
        ).event()
        await self.write_event(wyoming_info_event)
        return True

    async def _synthesize_pcm_chunks(self, synthesize: Synthesize) -> bool:
        logger.debug(synthesize)

        text = " ".join(synthesize.text.strip().splitlines())

        voice_id = synthesize.voice.name if synthesize.voice else None
        if voice_id is None:
            raise ValueError("No voice specified in Synthesize event")

        if self.engine.get_storage().get_voice(voice_id) is None:
            raise ValueError("No supported voice")

        send_start = True
        async for result in self.engine.synthesize_pcm_chunks(text, voice_id, "TEXT"):
            if send_start:
                await self.write_event(
                    AudioStart(
                        rate=result.sample_rate,
                        width=result.bytes_per_sample,
                        channels=result.channels,
                    ).event()
                )
                send_start = False

            await self.write_event(
                AudioChunk(
                    rate=result.sample_rate,
                    width=result.bytes_per_sample,
                    channels=result.channels,
                    audio=result.audio,
                ).event()
            )

        await self.write_event(AudioStop().event())

        return True
