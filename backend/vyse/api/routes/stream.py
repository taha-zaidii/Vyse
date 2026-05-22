"""WebSocket streams — live incidents + live annotated feed."""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

# A trivial in-memory pub/sub. In the orchestrated process, AnalyticsAgent
# pushes into this set; here we just connect WebSocket clients to it.
_connected: set[WebSocket] = set()


@router.websocket("/ws/stream/incidents")
async def stream_incidents(ws: WebSocket) -> None:
    await ws.accept()
    _connected.add(ws)
    try:
        while True:
            # Keep the connection open; broadcast happens via broadcast_incident().
            await asyncio.sleep(30)
            await ws.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    finally:
        _connected.discard(ws)


async def broadcast_incident(payload: dict) -> None:
    dead: list[WebSocket] = []
    for ws in _connected:
        try:
            await ws.send_json({"type": "incident", "data": payload})
        except Exception:
            dead.append(ws)
    for ws in dead:
        _connected.discard(ws)


@router.websocket("/ws/stream/feed/{camera_id}")
async def stream_feed(ws: WebSocket, camera_id: str) -> None:
    """Placeholder annotated-feed pump. Wire to Vision Agent shared buffer in P2."""
    await ws.accept()
    try:
        while True:
            await ws.send_json({"camera_id": camera_id, "type": "frame_placeholder"})
            await asyncio.sleep(1.0)
    except WebSocketDisconnect:
        pass
