import asyncio
import unittest.mock

import pytest

from src.tts.models import OpenAiNormalizationConfig
from src.tts.preprocessing.openai_text_normalizer import OpenAiTextNormalizer


class TestOpenAiTextNormalizer:
    """Tests for OpenAiTextNormalizer behavior."""

    async def test_single_chunk_normalized_successfully(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        result = [
            chunk
            async for chunk in normalizer.normalize_text(
                iter(["hello world"]), normalization_options
            )
        ]

        assert result == ["normalized text"]
        mock_openai_client.chat.completions.create.assert_called_once()

    async def test_multiple_chunks_yielded_in_order(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        async def slow_create(*args, **kwargs):
            content = (
                args[1]["content"]
                if len(args) > 1
                else kwargs.get("messages", [{}])[1].get("content", "")
            )
            await asyncio.sleep(0.05)
            response = unittest.mock.MagicMock()
            response.choices = [
                unittest.mock.MagicMock(
                    message=unittest.mock.MagicMock(content=f"normalized {content}")
                )
            ]
            return response

        mock_openai_client.chat.completions.create = slow_create

        result = [
            chunk
            async for chunk in normalizer.normalize_text(
                iter(["first", "second", "third"]), normalization_options
            )
        ]

        assert result == ["normalized first", "normalized second", "normalized third"]

    async def test_api_failure_falls_back_to_original(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        mock_openai_client.chat.completions.create = unittest.mock.AsyncMock(
            side_effect=RuntimeError("API error")
        )

        result = [
            chunk
            async for chunk in normalizer.normalize_text(
                iter(["hello world"]), normalization_options
            )
        ]

        assert result == ["hello world"]

    async def test_empty_response_falls_back_to_original(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        response = unittest.mock.MagicMock()
        response.choices = [unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="  "))]
        mock_openai_client.chat.completions.create = unittest.mock.AsyncMock(return_value=response)

        result = [
            chunk
            async for chunk in normalizer.normalize_text(
                iter(["hello world"]), normalization_options
            )
        ]

        assert result == ["hello world"]

    def test_negative_timeout_raises_value_error(self, mock_openai_client):
        config = OpenAiNormalizationConfig(
            timeout=-1,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        with pytest.raises(ValueError, match="timeout cannot be negative"):
            OpenAiTextNormalizer(client=mock_openai_client, config=config)

    def test_non_positive_max_concurrent_raises_value_error(self, mock_openai_client):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=0,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        with pytest.raises(
            ValueError, match="max_concurrent_sentences_per_request cannot be negative or zero"
        ):
            OpenAiTextNormalizer(client=mock_openai_client, config=config)

    async def test_empty_chunks_iterator_yields_nothing(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        result = [
            chunk async for chunk in normalizer.normalize_text(iter([]), normalization_options)
        ]

        assert result == []
        mock_openai_client.chat.completions.create.assert_not_called()

    async def test_semaphore_respects_concurrency_limit(
        self, mock_openai_client, normalization_options
    ):
        max_concurrent = 1
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=max_concurrent,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        concurrent_count = 0
        observed_max = 0

        async def tracking_create(*args, **kwargs):
            nonlocal concurrent_count, observed_max
            concurrent_count += 1
            observed_max = max(observed_max, concurrent_count)
            await asyncio.sleep(0.05)
            concurrent_count -= 1
            response = unittest.mock.MagicMock()
            response.choices = [
                unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="normalized"))
            ]
            return response

        mock_openai_client.chat.completions.create = tracking_create

        result = [
            chunk
            async for chunk in normalizer.normalize_text(
                iter(["a", "b", "c", "d"]), normalization_options
            )
        ]

        assert len(result) == 4
        # Chunk 0 bypasses the semaphore; subsequent chunks are bounded by max_concurrent
        assert observed_max <= max_concurrent + 1

    async def test_task_cancellation_on_generator_cleanup(
        self, mock_openai_client, normalization_options
    ):
        config = OpenAiNormalizationConfig(
            timeout=10.0,
            max_concurrent_sentences_per_request=4,
            default_model="gpt-4o-mini",
            default_prompt="Normalize text",
        )
        normalizer = OpenAiTextNormalizer(client=mock_openai_client, config=config)

        call_count = 0

        async def slow_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return unittest.mock.MagicMock(
                    choices=[
                        unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="first"))
                    ]
                )
            await asyncio.sleep(10)
            return unittest.mock.MagicMock(
                choices=[unittest.mock.MagicMock(message=unittest.mock.MagicMock(content="never"))]
            )

        mock_openai_client.chat.completions.create = slow_create

        gen = normalizer.normalize_text(iter(["first", "second", "third"]), normalization_options)

        first = await gen.__anext__()
        assert first == "first"

        await gen.aclose()

        assert call_count >= 1
