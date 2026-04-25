"""
Node health check via HTTP.
"""

import time as _time
from typing import Any

import httpx

from app.schemas import NodeHealthResponse


async def check_node_health(
    host: str,
    port: int,
    timeout: int = 10,
) -> NodeHealthResponse:
    """
    Check node health by calling its /health endpoint.
    Returns NodeHealthResponse with status, latency, and loaded models.
    """
    url = f"http://{host}:{port}/health"
    t0 = _time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=float(timeout)) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            latency = int((_time.monotonic() - t0) * 1000)
            return NodeHealthResponse(
                status=data.get("status", "ok"),
                latency_ms=latency,
                models_loaded=data.get("models_loaded", []),
            )
    except httpx.TimeoutException:
        latency = int((_time.monotonic() - t0) * 1000)
        return NodeHealthResponse(
            status="timeout",
            latency_ms=latency,
            models_loaded=[],
        )
    except httpx.ConnectError:
        latency = int((_time.monotonic() - t0) * 1000)
        return NodeHealthResponse(
            status="offline",
            latency_ms=latency,
            models_loaded=[],
        )
    except Exception as e:
        latency = int((_time.monotonic() - t0) * 1000)
        return NodeHealthResponse(
            status=f"error: {e}",
            latency_ms=latency,
            models_loaded=[],
        )
