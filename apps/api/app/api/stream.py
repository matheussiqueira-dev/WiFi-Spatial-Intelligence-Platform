"""Live WebSocket stream: origin check, first-frame auth, bounded per-subscriber queues."""

import asyncio
import time

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from app.api.deps import resolve_principal
from app.capabilities import is_enabled

# Personal tokens are re-checked on this cadence, so a revocation closes live streams.
REVALIDATE_SECONDS = 2.0

router = APIRouter()


@router.websocket("/api/v1/stream")
async def stream(ws: WebSocket):
    c = ws.app.state.container
    settings, store, pipeline, limiter = c.settings, c.store, c.pipeline, c.limiter
    handshakes = c.stream_handshakes
    if not is_enabled("spatial.presence", settings.capability_profile):
        await ws.close(code=1008, reason="capability spatial.presence disabled by profile")
        return
    if ws.headers.get("origin") not in settings.origins:
        await asyncio.to_thread(store.security_denial, "ws.origin_denied")
        await ws.close(code=1008)
        return
    # Pending handshakes hold a slot so the cap also bounds unauthenticated sockets.
    if len(pipeline.subscribers) + len(handshakes) >= 8:
        await asyncio.to_thread(store.security_denial, "ws.limit")
        await ws.close(code=1013)
        return
    peer = ws.client.host if ws.client else "local"
    # Legitimate reconnects use their own budget; "auth" counts only failed tokens.
    if limiter.check("stream", peer):
        await asyncio.to_thread(store.security_denial, "ws.rate_denied")
        await ws.close(code=1013)
        return
    queue: asyncio.Queue[dict] = asyncio.Queue(maxsize=16)
    handshake = object()
    handshakes.add(handshake)
    receiver = None
    pending = None
    try:
        await ws.accept()
        auth = await asyncio.wait_for(ws.receive_json(), timeout=settings.ws_auth_timeout_seconds)
        principal = (
            await resolve_principal(c, auth["token"])
            if isinstance(auth, dict) and isinstance(auth.get("token"), str)
            else None
        )
        # Every role may watch the stream; viewer is the minimum.
        if principal is None:
            limiter.check("auth", peer)
            await asyncio.to_thread(store.security_denial, "ws.auth_denied")
            await ws.close(code=1008)
            return
        handshakes.discard(handshake)
        pipeline.subscribers.add(queue)
        await ws.send_json({"type": "status", "data": pipeline.status()})

        async def receive_disconnect():
            while True:
                message = await ws.receive()
                if message["type"] == "websocket.disconnect":
                    return

        receiver = asyncio.create_task(receive_disconnect())
        checked = time.monotonic()
        while not receiver.done():
            if not principal.bootstrap and time.monotonic() - checked >= REVALIDATE_SECONDS:
                checked = time.monotonic()
                if not await asyncio.to_thread(c.access_tokens.active, principal.subject_id):
                    await ws.close(code=1008, reason="access token revoked")
                    break
            # One pending get survives heartbeats, so a dequeued event is never dropped.
            pending = pending or asyncio.create_task(queue.get())
            done, _ = await asyncio.wait(
                {pending, receiver}, timeout=2, return_when=asyncio.FIRST_COMPLETED
            )
            if receiver in done:
                break
            if pending in done:
                event, pending = pending.result(), None
                await asyncio.wait_for(ws.send_json({"type": "event", "data": event}), 5)
            else:
                await asyncio.wait_for(
                    ws.send_json({"type": "status", "data": pipeline.status()}), 5
                )
    except TimeoutError:
        if receiver is None:
            limiter.check("auth", peer)
            await asyncio.to_thread(store.security_denial, "ws.timeout")
            await ws.close(code=1008)
    except (ValueError, KeyError):
        # Malformed JSON or a binary first frame is a failed authentication attempt.
        limiter.check("auth", peer)
        await asyncio.to_thread(store.security_denial, "ws.auth_denied")
        await ws.close(code=1008)
    except (WebSocketDisconnect, RuntimeError):
        pass
    finally:
        handshakes.discard(handshake)
        pipeline.subscribers.discard(queue)
        for task in (pending, receiver):
            if task:
                task.cancel()
                await asyncio.gather(task, return_exceptions=True)
