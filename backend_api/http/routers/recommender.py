"""Recommender workflow routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend_api.http.schemas.common import JobResponse
from backend_api.http.schemas.recommender import (
    RagDecisionRequest,
    RecommenderHandoffRequest,
    RecommenderHandoffResponse,
    RecommenderStartRequest,
)
from backend_api.http.services.events import sse_response
from backend_api.http.services.job_store import job_store
from backend_api.http.services.recommender_service import (
    assess_rag,
    build_trimmer_handoff,
    get_recommender_state,
    start_recommender_job,
    submit_rag_decision,
)

router = APIRouter(prefix="/recommender", tags=["recommender"])


@router.post("/start", response_model=JobResponse)
def start_recommender(request: RecommenderStartRequest) -> JobResponse:
    job_id = start_recommender_job(
        request.file_content,
        request.file_name,
        request.model,
        request.step,
    )
    job = job_store.get(job_id)
    return JobResponse(job_id=job_id, module=job.module, status=job.status.value)


@router.get("/{job_id}/stream")
def stream_recommender(job_id: str) -> StreamingResponse:
    try:
        job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return sse_response(job_id)


@router.get("/{job_id}/state")
def recommender_state(job_id: str) -> dict:
    try:
        return get_recommender_state(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@router.post("/{job_id}/rag-decision", response_model=JobResponse)
def recommender_rag_decision(job_id: str, request: RagDecisionRequest) -> JobResponse:
    try:
        rag_job_id = submit_rag_decision(job_id, request.flags, request.model)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    job = job_store.get(rag_job_id)
    return JobResponse(job_id=rag_job_id, module=job.module, status=job.status.value)


@router.get("/{job_id}/rag-status")
def recommender_rag_status(job_id: str) -> dict:
    try:
        return assess_rag(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc


@router.post("/{job_id}/handoff", response_model=RecommenderHandoffResponse)
def recommender_handoff(job_id: str, request: RecommenderHandoffRequest) -> RecommenderHandoffResponse:
    try:
        handoff = build_trimmer_handoff(job_id, request.chosen_controller)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return RecommenderHandoffResponse(**handoff)
