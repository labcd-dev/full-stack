"""In-memory job tracking for long-running workflows."""

from __future__ import annotations

import queue
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional


class JobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    WAITING_INPUT = "waiting_input"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Job:
    id: str
    module: str
    status: JobStatus = JobStatus.PENDING
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_queue: queue.Queue = field(default_factory=queue.Queue)
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None
    thread: Optional[threading.Thread] = field(default=None, repr=False)

    def touch(self, status: Optional[JobStatus] = None) -> None:
        if status is not None:
            self.status = status
        self.updated_at = datetime.now(timezone.utc).isoformat()


class JobStore:
    def __init__(self) -> None:
        self._jobs: Dict[str, Job] = {}
        self._lock = threading.Lock()

    def create(self, module: str, metadata: Optional[Dict[str, Any]] = None) -> Job:
        job_id = str(uuid.uuid4())
        job = Job(id=job_id, module=module, metadata=metadata or {})
        with self._lock:
            self._jobs[job_id] = job
        return job

    def get(self, job_id: str) -> Job:
        with self._lock:
            job = self._jobs.get(job_id)
        if job is None:
            raise KeyError(job_id)
        return job

    def update_metadata(self, job_id: str, updates: Dict[str, Any]) -> Job:
        job = self.get(job_id)
        job.metadata.update(updates)
        job.touch()
        return job


job_store = JobStore()
