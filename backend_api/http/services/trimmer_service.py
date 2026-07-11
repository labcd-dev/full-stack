"""Trimmer HTTP service adapter."""

from __future__ import annotations

import logging
import threading
from typing import Any, Dict

from backend_api.Trimmer.build_graph import build_workflow_graph
from backend_api.Trimmer.services.human_input import HumanInputRequired, normalize_human_answer
from backend_api.Trimmer.workflow_helpers import build_trimmer_initial_state, finalize_trimmer_run
from backend_api.common.serialization import make_serializable
from backend_api.http.config import RESULTS_DIR
from backend_api.http.services.job_store import JobStatus, job_store


def _create_logger(job_id: str) -> logging.Logger:
    log_dir = RESULTS_DIR.parent / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(f"trimmer.{job_id}")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.FileHandler(log_dir / f"session_langraph_{job_id}.log")
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logger.addHandler(handler)
    return logger


def _trimmer_worker(job_id: str) -> None:
    job = job_store.get(job_id)
    graph = job.metadata["graph"]
    initial_state = job.metadata["initial_state"]

    try:
        job.touch(JobStatus.RUNNING)
        for mode, content in graph.stream(initial_state, stream_mode=["updates", "custom", "values"]):
            job.event_queue.put({"type": "stream", "mode": mode, "content": make_serializable(content)})
            if mode == "values":
                job.metadata["final_values"] = make_serializable(content)
        job.event_queue.put({"type": "done"})
        _finalize_job(job_id)
        job.touch(JobStatus.COMPLETED)
    except HumanInputRequired as exc:
        job.metadata["pending_request"] = exc.request
        job.event_queue.put({"type": "human_input", "content": exc.request})
        job.touch(JobStatus.WAITING_INPUT)
    except Exception as exc:
        job.error = str(exc)
        job.event_queue.put({"type": "error", "content": str(exc)})
        job.touch(JobStatus.FAILED)


def _finalize_job(job_id: str) -> None:
    job = job_store.get(job_id)
    final_values = job.metadata.get("final_values", {})
    if not final_values:
        return
    artifacts = finalize_trimmer_run(final_values, job.metadata["file_name"], str(RESULTS_DIR))
    job.metadata["artifacts"] = artifacts


def start_trimmer_job(
    file_content: str,
    file_name: str,
    model: str,
    trimming_params: Dict[str, Any],
) -> str:
    logger = _create_logger(file_name)
    initial_state = build_trimmer_initial_state(
        trimming_params,
        file_content,
        logger,
        ui_inputs={},
        ui_mode="api",
    )
    job = job_store.create(
        "trimmer",
        metadata={
            "file_name": file_name,
            "file_content": file_content,
            "model": model,
            "trimming_params": trimming_params,
            "graph": build_workflow_graph(model),
            "initial_state": initial_state,
            "ui_inputs": {},
            "logs": [],
        },
    )
    thread = threading.Thread(target=_trimmer_worker, args=(job.id,), daemon=True)
    job.thread = thread
    thread.start()
    return job.id


def submit_trimmer_input(job_id: str, key: str, prompt: str, answer: str) -> None:
    job = job_store.get(job_id)
    ui_inputs = job.metadata.setdefault("ui_inputs", {})
    ui_inputs[key] = normalize_human_answer(prompt, answer)
    job.metadata["pending_request"] = None

    initial_state = build_trimmer_initial_state(
        job.metadata["trimming_params"],
        job.metadata["file_content"],
        _create_logger(job_id),
        ui_inputs=ui_inputs,
        ui_mode="api",
    )
    job.metadata["initial_state"] = initial_state

    thread = threading.Thread(target=_trimmer_worker, args=(job.id,), daemon=True)
    job.thread = thread
    thread.start()


def get_trimmer_artifacts(job_id: str) -> Dict[str, Any]:
    job = job_store.get(job_id)
    return job.metadata.get("artifacts", {})
