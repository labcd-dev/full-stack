"""Recommender HTTP service adapter."""

from __future__ import annotations

import threading
from typing import Any, Dict, Optional

from backend_api.Recommender.build_graph import build_graph
from backend_api.Recommender.pipeline_handoff import prepare_trimmer_handoff
from backend_api.Recommender.rag.completion import assess_rag_completion
from backend_api.common.serialization import make_serializable
from backend_api.http.services.job_store import JobStatus, job_store


def _recommender_worker(job_id: str, step: str, graph_input: Optional[Dict[str, Any]]) -> None:
    job = job_store.get(job_id)
    graph = job.metadata["graph"]
    config = job.metadata["graph_config"]

    try:
        job.touch(JobStatus.RUNNING)
        for mode, content in graph.stream(graph_input, config, stream_mode=["updates", "custom"]):
            job.event_queue.put({"type": "stream", "mode": mode, "content": make_serializable(content)})
        job.event_queue.put({"type": "done", "step": step})
        job.touch(JobStatus.COMPLETED)
    except Exception as exc:
        job.error = str(exc)
        job.event_queue.put({"type": "error", "content": str(exc)})
        job.touch(JobStatus.FAILED)


def _start_worker(job: Any, step: str, graph_input: Optional[Dict[str, Any]]) -> None:
    thread = threading.Thread(
        target=_recommender_worker,
        args=(job.id, step, graph_input),
        daemon=True,
    )
    job.thread = thread
    thread.start()


def start_recommender_job(
    file_content: str,
    file_name: str,
    model: str,
    step: str = "initial_run",
) -> str:
    job = job_store.create(
        "recommender",
        metadata={
            "file_name": file_name,
            "file_content": file_content,
            "model": model,
            "step": step,
            "graph": build_graph(model),
            "graph_config": {"configurable": {"thread_id": ""}},
            "logs": [{"agent_tag": "Equation", "log_history": file_content}],
        },
    )
    job.metadata["graph_config"] = {"configurable": {"thread_id": job.id}}

    graph_input = (
        {"equation": file_content, "file_name": file_name, "messages": []}
        if step == "initial_run"
        else None
    )
    _start_worker(job, step, graph_input)
    return job.id


def submit_rag_decision(job_id: str, flags: list[str], model: str) -> str:
    job = job_store.get(job_id)
    graph = job.metadata["graph"]
    config = job.metadata["graph_config"]
    graph.update_state(config, {"RAG_decision": {"Flag": flags, "Model": model}})

    rag_job = job_store.create(
        "recommender",
        metadata={
            "file_name": job.metadata["file_name"],
            "file_content": job.metadata["file_content"],
            "model": job.metadata["model"],
            "step": "rag_run",
            "graph": graph,
            "graph_config": config,
            "parent_job_id": job_id,
            "logs": job.metadata.get("logs", []),
        },
    )
    _start_worker(rag_job, "rag_run", None)
    return rag_job.id


def get_recommender_state(job_id: str) -> Dict[str, Any]:
    job = job_store.get(job_id)
    graph = job.metadata["graph"]
    config = job.metadata["graph_config"]
    return make_serializable(graph.get_state(config).values)


def build_trimmer_handoff(job_id: str, chosen_controller: Optional[str] = None) -> Dict[str, Any]:
    state_snapshot = get_recommender_state(job_id)
    return prepare_trimmer_handoff(state_snapshot, chosen_controller)


def assess_rag(job_id: str) -> Dict[str, Optional[str]]:
    job = job_store.get(job_id)
    return assess_rag_completion(job.metadata["file_name"])
