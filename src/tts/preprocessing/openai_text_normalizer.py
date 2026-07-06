import asyncio
from collections.abc import AsyncIterator, Iterator

from loguru import logger
from openai import AsyncOpenAI

from src.tts.models import NormalizationOptions, OpenAiNormalizationConfig
from src.tts.preprocessing.text_normalizer import TextNormalizer


class OpenAiTextNormalizer(TextNormalizer):
    def __init__(self, client: AsyncOpenAI, config: OpenAiNormalizationConfig | None = None):
        if config is None:
            config = OpenAiNormalizationConfig()

        if config.timeout < 0:
            raise ValueError("timeout cannot be negative")

        if config.max_concurrent_chunks_per_request <= 0:
            raise ValueError("max_concurrent_chunks_per_request cannot be negative or zero")

        self._options = config
        self._client = client

    async def _normalize_text(self, text: str) -> str:
        try:
            response = await asyncio.wait_for(
                self._client.chat.completions.create(
                    model=self._options.default_model,
                    messages=[
                        {"role": "system", "content": self._options.default_promt},
                        {"role": "user", "content": text},
                    ],
                    temperature=0.0,
                    reasoning_effort="none",
                    extra_body={"think": False},
                ),
                timeout=self._options.timeout,
            )

            clean_text = response.choices[0].message.content.strip()

            if not clean_text:
                logger.warning(
                    "{model_name} returned an empty response. Using original text",
                    model_name=self._options.default_model,
                )
            else:
                return clean_text
        except Exception:
            logger.exception(
                "{model_name} normalization failed with error. Returning original text",
                model_name=self._options.default_model,
            )

        return text

    async def _normalize_chunk(
        self,
        index: int,
        text: str,
        result_dict: dict,
        event: asyncio.Event,
    ):
        logger.debug(
            "Send chunk {index} to {model_name}. Text: {text}",
            model_name=self._options.default_model,
            index=index,
            text=text,
        )
        try:
            result_dict[index] = await self._normalize_text(text)
        finally:
            event.set()

    async def normalize_text(
        self, chunks: Iterator[str], options: NormalizationOptions
    ) -> AsyncIterator[str]:
        """Return a normalized string from raw text."""
        result_dict = {}
        tasks = []
        events = {}

        semaphore = asyncio.Semaphore(self._options.max_concurrent_chunks_per_request)

        async def normalize_chunk_concurrently(index: int, text: str):
            async with semaphore:
                await self._normalize_chunk(index, text, result_dict, events[index])

        next_index_to_yield = 0
        chunk_index = 0

        try:
            for chunk in chunks:
                events[chunk_index] = asyncio.Event()

                if chunk_index == 0:
                    # Instantly send Chunk #0 without semaphore restrictions
                    tasks.append(
                        asyncio.create_task(self._normalize_chunk(0, chunk, result_dict, events[0]))
                    )
                    # Micro-pause to ensure Chunk #0 request reaches the network first
                    await asyncio.sleep(0.001)
                else:
                    # All other chunks are sent to background competitive processing
                    tasks.append(
                        asyncio.create_task(normalize_chunk_concurrently(chunk_index, chunk))
                    )

                chunk_index += 1

                while next_index_to_yield in events and events[next_index_to_yield].is_set():
                    logger.debug("Chunk {index} processed", index=chunk_index)
                    yield result_dict.pop(next_index_to_yield)
                    events.pop(next_index_to_yield)
                    next_index_to_yield += 1

            total_chunks = chunk_index

            if total_chunks == 0:
                return

            for i in range(next_index_to_yield, total_chunks):
                await events[i].wait()
                logger.debug("Chunk {index} processed", index=i)
                yield result_dict.pop(i)
        finally:
            for task in tasks:
                if not task.done():
                    task.cancel()
