"""Bounded per-process fixed-window limits. No trust in forwarded client headers."""

import math
import time
from collections import OrderedDict
from threading import Lock


class BodyLimit:
    """Reject request bodies above a fixed size before any parsing or authentication."""

    def __init__(self, app, limit=65536):
        self.app = app
        self.limit = limit

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        length = dict(scope["headers"]).get(b"content-length")
        if length is not None and (not length.isdigit() or int(length) > self.limit):
            return await self.reject(send)
        received = 0
        rejected = False

        async def bounded_receive():
            nonlocal received, rejected
            message = await receive()
            if message["type"] == "http.request":
                received += len(message.get("body", b""))
                if received > self.limit:
                    rejected = True
                    raise BodyTooLarge
            return message

        started = False

        async def tracked_send(message):
            # Frameworks may turn the receive error into their own 400; answer 413 instead.
            nonlocal started
            if rejected:
                if not started:
                    started = True
                    await self.reject(send)
                return
            started = started or message["type"] == "http.response.start"
            await send(message)

        try:
            await self.app(scope, bounded_receive, tracked_send)
        except BodyTooLarge:
            if not started:
                await self.reject(send)
        except Exception:
            if not rejected:
                raise
            if not started:
                await self.reject(send)

    @staticmethod
    async def reject(send):
        await send(
            {
                "type": "http.response.start",
                "status": 413,
                "headers": [(b"content-type", b"application/json"), (b"connection", b"close")],
            }
        )
        await send({"type": "http.response.body", "body": b'{"detail":"request body too large"}'})


class BodyTooLarge(Exception):
    pass


class LocalLimiter:
    def __init__(self, limits, seconds=60, capacity=1024, clock=time.monotonic):
        self.limits = limits
        self.seconds = seconds
        self.capacity = capacity
        self.clock = clock
        self.entries = OrderedDict()
        self.lock = Lock()

    def check(self, category: str, peer: str) -> int:
        with self.lock:
            now = self.clock()
            while self.entries and next(iter(self.entries.values()))[0] <= now:
                self.entries.popitem(last=False)
            key = peer
            entry = self.entries.get(key)
            if entry is None:
                if len(self.entries) >= self.capacity:
                    return max(1, math.ceil(next(iter(self.entries.values()))[0] - now))
                entry = [now + self.seconds, {name: 0 for name in self.limits}]
                self.entries[key] = entry
            if entry[1][category] >= self.limits[category]:
                return max(1, math.ceil(entry[0] - now))
            entry[1][category] += 1
            return 0
