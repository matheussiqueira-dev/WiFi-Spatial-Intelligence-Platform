"""Ports the ingestion pipeline actually relies on (previously implicit duck typing)."""

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class SourceProvider(Protocol):
    streaming: bool
    connected: bool
    config: Any
    tick: int

    async def connect(self) -> None: ...

    async def disconnect(self) -> None: ...


@runtime_checkable
class SampledSource(SourceProvider, Protocol):
    """Pulled once per tick under the control lock (synthetic-native)."""

    def sample(self) -> Any: ...


@runtime_checkable
class StreamingSource(SourceProvider, Protocol):
    """Awaited outside the control lock (legacy laboratory stream)."""

    duplicates: int

    async def next_event(self) -> Any: ...

    def diagnostics(self) -> dict: ...
