"""SiloDesigner HTTP service adapter."""

from __future__ import annotations

import threading
from typing import Any, Dict

from backend_api.SiloDesigner.app import (
    DesignCancelledError,
    DesignMonitor,
    get_serializable_monitor_state,
    run_design_with_monitoring,
)
from backend_api.SiloDesigner.config import build_design_config
from backend_api.common.serialization import make_serializable
from backend_api.http.services.job_store import JobStatus, job_store

MONITOR_PUBLISH_INTERVAL_SECONDS = 3.0


def _monitor_publisher(job_id: str, monitor: DesignMonitor, stop_event: threading.Event) -> None:
    """Push monitor snapshots to the SSE queue while the design job is running."""
    last_published_revision = -1
    last_progress_count = 0
    last_llm_count = 0

    while not stop_event.wait(MONITOR_PUBLISH_INTERVAL_SECONDS):
        try:
            job = job_store.get(job_id)
            if job.status in {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED}:
                break

            progress_history = monitor.progress_history
            progress_changed = len(progress_history) != last_progress_count
            revision_changed = monitor.revision != last_published_revision
            llm_responses = monitor.llm_responses
            llm_changed = len(llm_responses) != last_llm_count

            if progress_changed:
                new_entries = progress_history[last_progress_count:]
                for entry in new_entries:
                    timestamp = entry.get("timestamp", "")
                    message = entry.get("message", "")
                    job.event_queue.put(
                        {
                            "type": "stream",
                            "content": {
                                "agent_tag": "SiloDesigner",
                                "log_history": f"[{timestamp}] {message}",
                            },
                        }
                    )

                latest_message = (
                    progress_history[-1].get("message", "Running single-loop design...")
                    if progress_history
                    else "Running single-loop design..."
                )
                job.event_queue.put(
                    {
                        "type": "stream",
                        "content": {
                            "text": latest_message,
                            "progress": min(len(progress_history) * 5, 95) / 100.0,
                        },
                    }
                )
                last_progress_count = len(progress_history)

            if llm_changed:
                for entry in llm_responses[last_llm_count:]:
                    job.event_queue.put(
                        {
                            "type": "stream",
                            "content": {
                                "agent_tag": entry.get("agent", "LLM Agent"),
                                "log_history": entry.get("response", ""),
                            },
                        }
                    )
                last_llm_count = len(llm_responses)

            if revision_changed:
                state = get_serializable_monitor_state(monitor)
                job.event_queue.put({"type": "monitor", "content": state})
                last_published_revision = monitor.revision
        except KeyError:
            break


def _silo_worker(job_id: str) -> None:
    job = job_store.get(job_id)
    config = job.metadata["config"]
    monitor = job.metadata["monitor"]
    stop_event = threading.Event()
    publisher = threading.Thread(
        target=_monitor_publisher,
        args=(job_id, monitor, stop_event),
        daemon=True,
    )
    publisher.start()

    try:
        job.touch(JobStatus.RUNNING)
        run_design_with_monitoring(config, monitor)
        job.metadata["monitor_state"] = get_serializable_monitor_state(monitor)
        job.event_queue.put({"type": "monitor", "content": job.metadata["monitor_state"]})
        job.touch(JobStatus.COMPLETED)
    except DesignCancelledError:
        job.metadata["monitor_state"] = get_serializable_monitor_state(monitor)
        job.event_queue.put({"type": "monitor", "content": job.metadata["monitor_state"]})
        job.error = "Design cancelled by user"
        job.touch(JobStatus.CANCELLED)
    except Exception as exc:
        job.error = str(exc)
        job.event_queue.put({"type": "error", "content": str(exc)})
        job.touch(JobStatus.FAILED)
    finally:
        stop_event.set()
        publisher.join(timeout=1.0)


def start_silo_job(config: Dict[str, Any], control_objective: str = "") -> str:
    runtime_config = build_design_config(
        config,
        control_objective=control_objective,
        file_content=config.get("file_content"),
        custom_dynamics_path=config.get("custom_dynamics_path"),
        file_type=config.get("file_type", "Python (.py)"),
    )
    monitor = DesignMonitor()
    job = job_store.create(
        "silo",
        metadata={
            "config": runtime_config,
            "monitor": monitor,
        },
    )
    thread = threading.Thread(target=_silo_worker, args=(job.id,), daemon=True)
    job.thread = thread
    thread.start()
    return job.id


def get_silo_monitor_state(job_id: str) -> Dict[str, Any]:
    job = job_store.get(job_id)
    monitor = job.metadata["monitor"]
    return make_serializable(get_serializable_monitor_state(monitor))
