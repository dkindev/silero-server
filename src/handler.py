import logging
import re

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

from src.tts.engine import BYTES_PER_SAMPLE, CHANNELS, SileroTTSEngine

_LOGGER = logging.getLogger(__name__)


def _get_language_from_locale_string(locale_str: str) -> str | None:
    if not locale_str:
        return None
    parts = re.split(r"[_.-]", locale_str)
    return parts[0] if parts else None


def _create_wyoming_info(engine: SileroTTSEngine) -> Info:
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
            )
        )

    voices.sort(key=lambda v: v.name)

    return Info(
        tts=[
            TtsProgram(
                name="silero",
                description="A fast, local, neural text to speech engine",
                attribution=Attribution(
                    name="silero",
                    url="https://github.com/snakers4/silero-models",
                ),
                installed=True,
                voices=voices,
            )
        ],
    )


class SileroWyomingHandler(AsyncEventHandler):
    def __init__(
        self,
        engine: SileroTTSEngine,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.engine = engine
        self.is_streaming: bool | None = None
        self._synthesize: Synthesize | None = None

    async def handle_event(self, event: Event) -> bool:
        if Describe.is_type(event.type):
            wyoming_info_event = _create_wyoming_info(self.engine).event()
            await self.write_event(wyoming_info_event)
            _LOGGER.debug("Sent info")
            return True

        try:
            if Synthesize.is_type(event.type):
                if self.is_streaming:
                    return True

                synthesize = Synthesize.from_event(event)
                self._synthesize = Synthesize(text="", voice=synthesize.voice)
                await self._handle_synthesize(self._synthesize)
                return True

            if SynthesizeStart.is_type(event.type):
                stream_start = SynthesizeStart.from_event(event)
                self.is_streaming = True
                self._synthesize = Synthesize(text="", voice=stream_start.voice)
                _LOGGER.debug("Text stream started: voice=%s", stream_start.voice)
                return True

            if SynthesizeChunk.is_type(event.type):
                assert self._synthesize is not None
                stream_chunk = SynthesizeChunk.from_event(event)
                self._synthesize.text += stream_chunk.text
                return True

            if SynthesizeStop.is_type(event.type):
                assert self._synthesize is not None
                await self._handle_synthesize(self._synthesize)
                await self.write_event(SynthesizeStopped().event())
                _LOGGER.debug("Text stream stopped")
                return True

            return True
        except Exception as err:
            await self.write_event(Error(text=str(err), code=err.__class__.__name__).event())
            raise

    async def _handle_synthesize(self, synthesize: Synthesize) -> bool:
        _LOGGER.debug(synthesize)

        text = " ".join(synthesize.text.strip().splitlines())

        voice_id = synthesize.voice.name if synthesize.voice else None
        if voice_id is None:
            raise ValueError("No voice specified in Synthesize event")

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

        if send_start:
            await self.write_event(
                AudioStart(
                    rate=0,
                    width=BYTES_PER_SAMPLE,
                    channels=CHANNELS,
                ).event()
            )

        await self.write_event(AudioStop().event())
        _LOGGER.info("Synthesis complete")
        return True
