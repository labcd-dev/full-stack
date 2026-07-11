"""SiloDesigner workflow routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend_api.http.schemas.common import JobResponse
from backend_api.http.schemas.silo import SiloStartRequest
from backend_api.http.services.events import sse_response
from backend_api.http.services.job_store import job_store
from backend_api.http.services.silo_service import get_silo_monitor_state, start_silo_job

router = APIRouter(prefix="/silo", tags=["silo"])


@router.post("/start", response_model=JobResponse)
def start_silo(request: SiloStartRequest) -> JobResponse:
    job_id = start_silo_job(request.config, request.control_objective or "")
    job = job_store.get(job_id)
    return JobResponse(job_id=job_id, module=job.module, status=job.status.value)


@router.get("/{job_id}/stream")
def stream_silo(job_id: str) -> StreamingResponse:
    try:
        job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return sse_response(job_id)


@router.get("/{job_id}/monitor")
def silo_monitor(job_id: str) -> dict:
    try:
        return get_silo_monitor_state(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
