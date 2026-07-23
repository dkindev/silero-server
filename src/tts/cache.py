import asyncio
import math
from collections.abc import Callable
from typing import Any

from loguru import logger


class ExponentialDecayCache:
    def __init__(
        self,
        capacity: int,
        half_life_seconds: float = 5.0,
        eviction_interval: float | None = None,
        on_evict: Callable[[tuple[Any, Any]], None] | None = None,
    ):
        self._closed = False
        self._capacity = capacity

        # Half-life: During this period of inactivity, the RPS of the element will decrease by half
        self._half_life = half_life_seconds
        # Lambda for the exponential decay formula
        self._lambda_decay = math.log(2) / self._half_life

        self._on_evict = on_evict
        self._eviction_queue = asyncio.Queue()
        self._eviction_interval = eviction_interval
        self._cleaner_task = asyncio.create_task(self._cleaner_worker()) if self._on_evict else None

        self._cache = {}
        # Metadata: {key: {"score": current_RPS_score, "last_updated": last_updated_timestamp}}
        self._meta = {}

    @property
    def is_closed(self) -> bool:
        return self._closed

    async def _cleaner_worker(self):
        while True:
            try:
                (batch, should_stop) = await self._get_batch()

                if not batch:
                    continue

                try:
                    await asyncio.to_thread(self._on_evict, batch)
                except asyncio.CancelledError:
                    raise
                except Exception:
                    logger.exception("Eviction callback failed")

                self._close_batch(batch)

                if should_stop:
                    break
            except asyncio.CancelledError:
                logger.warning("Background cleanup worker was forcibly cancelled.")

                (batch, _) = self._get_batch_nowait()

                if batch:
                    try:
                        # call synchronously
                        self._on_evict(batch)
                    except Exception:
                        logger.exception("Emergency eviction cleanup failed")

                    self._close_batch(batch)

                raise

    async def _get_batch(self) -> tuple[list, bool]:
        interval = self._eviction_interval
        if interval and interval > 0:
            await asyncio.sleep(interval)

            if self._eviction_queue.empty():
                return (None, False)

            (batch, should_stop) = self._get_batch_nowait()
        else:
            first_item = await self._eviction_queue.get()
            (batch, should_stop) = self._get_batch_nowait()

            if first_item is None:
                should_stop = True
                self._eviction_queue.task_done()
            else:
                batch.append(first_item)

        return (batch, should_stop)

    def _get_batch_nowait(self) -> tuple[list, bool]:
        batch = []
        should_stop = False

        while not self._eviction_queue.empty():
            try:
                item = self._eviction_queue.get_nowait()

                if item is None:
                    should_stop = True
                    self._eviction_queue.task_done()
                    continue

                batch.append(item)
            except asyncio.QueueEmpty:
                break

        return (batch, should_stop)

    def _close_batch(self, batch: list):
        for _ in range(len(batch)):
            self._eviction_queue.task_done()

    def _decay_score(self, key: str, current_time: float) -> float:
        """Recalculates the current RPS rating of an element taking into account the elapsed time."""
        key_metadata = self._meta[key]
        delta_t = current_time - key_metadata["last_updated"]

        if delta_t <= 0:
            return key_metadata["score"]

        # Attenuation formula: score * e^(-lambda * delta_t)
        decayed_score = key_metadata["score"] * math.exp(-self._lambda_decay * delta_t)
        return decayed_score

    def _update_score(self, key: str, current_time: float):
        current_score = self._decay_score(key, current_time)

        # Updating metadata: faded rating + 1 new request
        self._meta[key] = {"score": current_score + 1.0, "last_updated": current_time}

    def _evict_lowest_element(self, current_time: float):
        min_score = float("inf")
        key_to_evict = None

        for k in self._cache.keys():
            score_now = self._decay_score(k, current_time)
            if score_now < min_score:
                min_score = score_now
                key_to_evict = k

        if key_to_evict is not None:
            evicted_value = self._cache[key_to_evict]

            del self._cache[key_to_evict]
            del self._meta[key_to_evict]

            self._eviction_queue.put_nowait((key_to_evict, evicted_value))

    def __len__(self) -> int:
        return len(self._cache)

    def get(self, key):
        """Gets value by key."""
        if key not in self._cache:
            return None

        current_time = asyncio.get_running_loop().time()
        self._update_score(key, current_time)

        return self._cache[key]

    def put(self, key: Any, value: Any) -> None:
        """Adds or updates element."""
        if self._closed:
            raise RuntimeError("cache is closed")
        if self._capacity <= 0:
            return

        current_time = asyncio.get_running_loop().time()

        if key in self._cache:
            self._cache[key] = value
            self._update_score(key, current_time)
            return

        if len(self._cache) >= self._capacity:
            self._evict_lowest_element(current_time)

        self._cache[key] = value
        self._meta[key] = {"score": 1.0, "last_updated": current_time}

    def clear(self):
        """Clears cache."""
        for key, value in self._cache.items():
            self._eviction_queue.put_nowait((key, value))

        self._cache.clear()
        self._meta.clear()

    async def close(self):
        """Clears cache and close the underlying clean up task.

        The cache will *not* be usable after this.
        """
        if self._closed:
            return

        self._closed = True

        self.clear()

        # signal to stop clean up task
        self._eviction_queue.put_nowait(None)

        # waiting for all items to be evicted
        try:
            if self._cleaner_task:
                await self._cleaner_task
        except asyncio.CancelledError:
            logger.warning(
                "close() method was canceled externally. Forcefully terminating the worker..."
            )

            if self._cleaner_task and not self._cleaner_task.done():
                self._cleaner_task.cancel()
            try:
                await self._cleaner_task
            except asyncio.CancelledError:
                pass

            raise
        finally:
            self._cleaner_task = None
            logger.info("Сache was closed successfully, resources were released.")
