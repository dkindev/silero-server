import asyncio
import math
from collections.abc import Callable
from typing import Any


class ExponentialDecayCache:
    def __init__(
        self,
        capacity: int,
        half_life_seconds: float = 5.0,
        on_evict: Callable[[tuple[Any, Any]], None] | None = None,
    ):
        self._capacity = capacity

        # Half-life: During this period of inactivity, the RPS of the element will decrease by half
        self._half_life = half_life_seconds
        # Lambda for the exponential decay formula
        self._lambda_decay = math.log(2) / self._half_life

        self._on_evict = on_evict
        self._eviction_queue = asyncio.Queue()
        self._cleaner_task = asyncio.create_task(self._cleaner_worker())

        self._cache = {}
        # Metadata: {key: {"score": current_RPS_score, "last_updated": last_updated_timestamp}}
        self._meta = {}

    async def _cleaner_worker(self):
        while True:
            first_item = await self._eviction_queue.get()

            should_stop = False

            if first_item is None:
                should_stop = True
                self._eviction_queue.task_done()

            batch = [first_item]

            while not self._eviction_queue.empty():
                item = self._eviction_queue.get_nowait()
                if item is None:
                    should_stop = True
                    self._eviction_queue.task_done()
                    continue
                batch.append(item)

            await asyncio.to_thread(self._on_evict, batch)

            for _ in range(len(batch)):
                self._eviction_queue.task_done()

            if should_stop:
                break

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

    async def clear(self):
        """Clears cache."""
        for key, value in self._cache.items():
            self._eviction_queue.put_nowait((key, value))

        self._cache.clear()
        self._meta.clear()

        # shutdown signal
        self._eviction_queue.put_nowait(None)

        await self._cleaner_task
