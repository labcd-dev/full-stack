"""Server-sent event helpers for workflow streaming."""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Generator, Iterable

from fastapi.responses import StreamingResponse

from backend_api.common.serialization import make_serializable
from backend_api.http.services.job_store import Job, JobStatus, job_store

SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "Connection": "keep-alive",
    "X-Accel-Buffering": "no",
}

KEEPALIVE_INTERVAL = 15.0


def format_sse(event: str, data: Dict[str, Any]) -> str:
    payload = json.dumps(make_serializable(data), default=str)
    return f"event: {event}\ndata: {payload}\n\n"


def sse_response(job_id: str) -> StreamingResponse:
    """Return a StreamingResponse configured for long-lived SSE connections."""
    return StreamingResponse(
        stream_job_events(job_id),
        media_type="text/event-stream",
        headers=SSE_HEADERS,
    )


def stream_job_events(job_id: str, poll_interval: float = 0.1) -> Generator[str, None, None]:
    """Yield SSE events until the job completes or fails."""
    job = job_store.get(job_id)
    yield format_sse("status", {"job_id": job_id, "status": job.status.value})
    last_activity = time.monotonic()

    while True:
        job = job_store.get(job_id)
        while not job.event_queue.empty():
            message = job.event_queue.get_nowait()
            event_type = message.get("type", "message")
            yield format_sse(event_type, message)
            last_activity = time.monotonic()

        job = job_store.get(job_id)
        if job.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
            yield format_sse(
                "done",
                {
                    "job_id": job_id,
                    "status": job.status.value,
                    "error": job.error,
                    "metadata": job_store.public_metadata(job),
                },
            )
            break

        if time.monotonic() - last_activity >= KEEPALIVE_INTERVAL:
            yield format_sse("ping", {"ts": time.time()})
            last_activity = time.monotonic()

        time.sleep(poll_interval)


def drain_events(job: Job, max_items: int = 100) -> Iterable[Dict[str, Any]]:
    count = 0
    while count < max_items and not job.event_queue.empty():
        yield job.event_queue.get_nowait()
        count += 1
