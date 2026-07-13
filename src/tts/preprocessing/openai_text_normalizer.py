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

        if config.max_concurrent_sentences_per_request <= 0:
            raise ValueError("max_concurrent_sentences_per_request cannot be negative or zero")

        self._options = config
        self._client = client

    async def normalize_text(
        self, sentences: Iterator[str], options: NormalizationOptions
    ) -> AsyncIterator[str]:
        """Return a normalized string from raw text."""
        queue = asyncio.Queue(maxsize=10)
        active_tasks = set()

        producer_task = asyncio.create_task(
            self._queue_sentences(
                sentences,
                queue,
                active_tasks,
            )
        )

        active_tasks.add(producer_task)
        producer_task.add_done_callback(active_tasks.discard)

        try:
            while True:
                future = await queue.get()
                if future is None:
                    queue.task_done()
                    break

                try:
                    yield await future
                finally:
                    queue.task_done()
        finally:
            tasks_to_cancel = [task for task in active_tasks if not task.done()]

            for task in tasks_to_cancel:
                task.cancel()

            if tasks_to_cancel:
                await asyncio.gather(*tasks_to_cancel, return_exceptions=True)

    async def _queue_sentences(
        self,
        sentences: Iterator[str],
        queue: asyncio.Queue,
        active_tasks: set,
    ):
        semaphore = asyncio.Semaphore(self._options.max_concurrent_sentences_per_request)

        loop = asyncio.get_running_loop()

        try:
            for sentence in sentences:
                future = loop.create_future()

                await queue.put(future)

                logger.debug("Sentence queued for normalizing. Text: {sentence}", sentence=sentence)

                task = asyncio.create_task(self._process_sentence(sentence, semaphore, future))

                active_tasks.add(task)
                task.add_done_callback(active_tasks.discard)

        finally:
            # Completion marker
            await queue.put(None)

    async def _process_sentence(
        self,
        sentence: str,
        semaphore: asyncio.Semaphore,
        future: asyncio.Future,
    ) -> str:
        try:
            async with semaphore:
                normalized_sentence = await asyncio.wait_for(
                    self._normalize_text(sentence),
                    timeout=self._options.timeout,
                )

                if not future.cancelled():
                    future.set_result(normalized_sentence)
        except Exception as e:
            if not future.cancelled():
                future.set_exception(e)

    async def _normalize_text(self, text: str) -> str:
        try:
            response = await self._client.chat.completions.create(
                model=self._options.default_model,
                messages=[
                    {"role": "system", "content": self._options.default_promt},
                    {"role": "user", "content": text},
                ],
                temperature=0.0,
                reasoning_effort="none",
                extra_body={"think": False},
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
