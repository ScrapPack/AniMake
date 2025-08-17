import uuid
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, Any, Callable

_executor = ThreadPoolExecutor(max_workers=4)


class Job:
    def __init__(self, fn: Callable, *, args=(), kwargs=None):
        self.id = str(uuid.uuid4())
        self.status = "queued"
        self.result: Any = None
        self.error: str | None = None
        self._queue: asyncio.Queue = asyncio.Queue()
        self._fn = fn
        self._args = args
        self._kwargs = kwargs or {}

    async def log(self, pct: int, msg: str):
        await self._queue.put({"pct": pct, "msg": msg})

    async def run(self, loop: asyncio.AbstractEventLoop):
        self.status = "running"
        try:
            def _run_blocking():
                def logger(p, m):
                    asyncio.run_coroutine_threadsafe(self.log(p, m), loop).result()
                return self._fn(logger, *self._args, **self._kwargs)

            self.result = await loop.run_in_executor(_executor, _run_blocking)
            self.status = "done"
            await self.log(100, "done")
        except Exception as e:  # noqa: BLE001
            self.status = "error"
            self.error = str(e)
            await self.log(100, f"error: {e}")


_jobs: Dict[str, Job] = {}


def create_job(fn: Callable, *, args=(), kwargs=None) -> Job:
    j = Job(fn, args=args, kwargs=kwargs)
    _jobs[j.id] = j
    return j


def get_job(job_id: str) -> Job | None:
    return _jobs.get(job_id)


