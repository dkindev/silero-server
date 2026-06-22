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
from src.tts.models import TextFormat


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
        throw_detailed_errors: bool,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.engine = engine
        self.supports_synthesize_streaming = supports_synthesize_streaming
        self.throw_detailed_errors = throw_detailed_errors
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

            error = (
                Error(text=str(err), code=err.__class__.__name__)
                if self.throw_detailed_errors
                else Error(text="Internal Server Error")
            )

            await self.write_event(error.event())

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

        text = synthesize.text.strip()
        if not text:
            await self.write_event(Error(text="Text is empty or whitespace").event())
            return False

        voice_id = synthesize.voice.name if synthesize.voice else None
        if not voice_id:
            await self.write_event(Error(text="No voice specified in Synthesize event").event())
            return False

        if not self.engine.get_storage().get_voice(voice_id):
            await self.write_event(Error(text=f"Unsupported voice: {voice_id}").event())
            return False

        text_format = TextFormat.TEXT

        # todo: add text_format field in next Wyoming protocol release
        # see https://github.com/OHF-Voice/wyoming/issues/38
        if hasattr(synthesize, "text_format"):
            req_text_format: str = synthesize.text_format

            supported_formats = [
                supported_format.value
                for supported_format in self.engine.get_supported_text_formats()
            ]
            if req_text_format in supported_formats:
                text_format = TextFormat(req_text_format)
            else:
                await self.write_event(
                    Error(text=f"Unsupported text format: {req_text_format}").event()
                )
                return False

        send_start = True
        async for result in self.engine.synthesize_pcm_chunks(text, voice_id, text_format):
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
