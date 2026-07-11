"""MuloDesigner HTTP service adapter."""

from __future__ import annotations

import threading
from typing import Any, Dict, List

from backend_api.MuloDesigner.GaAgent.data import apply_ga_event, empty_plot_data
from backend_api.MuloDesigner.GaAgent.src.callbacks import register_callback, unregister_callback
from backend_api.MuloDesigner.design_controller import MuloControllerDesigner
from backend_api.common.serialization import make_serializable
from backend_api.http.services.job_store import JobStatus, job_store

DEFAULT_MULO_RUN_CONFIG: Dict[str, Any] = {
    "case_study_file": "",
    "seed": 42,
    "llm_model": "gpt-4o-mini",
    "web_search_model": None,
    "max_attempts": 5,
    "buffer_size": 3,
    "max_wall_clock": 120.0,
    "max_cost_budget": 1.0,
    "prompt_variant": "elaborate",
}


def normalize_run_config(run_config: Dict[str, Any]) -> Dict[str, Any]:
    """Merge caller overrides with safe defaults for the GA workflow."""
    merged = {**DEFAULT_MULO_RUN_CONFIG, **(run_config or {})}
    merged["max_attempts"] = max(int(merged.get("max_attempts", 5)), 1)
    return merged


def _mulo_worker(job_id: str) -> None:
    job = job_store.get(job_id)
    designer = job.metadata["designer"]
    plot_data = job.metadata["plot_data"]

    def _push(event: Dict[str, Any]) -> None:
        updates = apply_ga_event(plot_data, event)
        job.metadata["plot_data"] = plot_data
        job.metadata.update(updates)
        job.event_queue.put({"type": "ga_event", "content": make_serializable(event)})

    try:
        job.touch(JobStatus.RUNNING)
        register_callback(_push)
        final_state = designer.design_controller()
        job.metadata["final_state"] = make_serializable(final_state)
        job.event_queue.put({"type": "run_complete", "final_state": job.metadata["final_state"]})
        job.touch(JobStatus.COMPLETED)
    except Exception as exc:
        job.error = str(exc)
        job.event_queue.put({"type": "run_error", "error": str(exc)})
        job.touch(JobStatus.FAILED)
    finally:
        unregister_callback()


def start_mulo_job(
    run_config: Dict[str, Any],
    controller_structure: List[Dict[str, Any]],
    system_identification: Dict[str, Any],
    trimming_result: Dict[str, Any],
    equation: str,
) -> str:
    normalized_run_config = normalize_run_config(run_config)
    designer = MuloControllerDesigner(
        normalized_run_config,
        controller_structure,
        system_identification,
        trimming_result,
        equation,
    )
    job = job_store.create(
        "mulo",
        metadata={
            "designer": designer,
            "plot_data": empty_plot_data(),
            "run_config": normalized_run_config,
        },
    )
    thread = threading.Thread(target=_mulo_worker, args=(job.id,), daemon=True)
    job.thread = thread
    thread.start()
    return job.id


def get_mulo_plot_data(job_id: str) -> Dict[str, Any]:
    job = job_store.get(job_id)
    return make_serializable(job.metadata.get("plot_data", {}))
