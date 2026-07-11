"""MuloDesigner workflow routes."""

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend_api.http.schemas.common import JobResponse
from backend_api.http.schemas.mulo import MuloStartRequest
from backend_api.http.services.events import sse_response
from backend_api.http.services.job_store import job_store
from backend_api.http.services.mulo_service import get_mulo_plot_data, start_mulo_job

router = APIRouter(prefix="/mulo", tags=["mulo"])


@router.post("/start", response_model=JobResponse)
def start_mulo(request: MuloStartRequest) -> JobResponse:
    job_id = start_mulo_job(
        request.run_config,
        request.controller_structure,
        request.system_identification,
        request.trimming_result,
        request.equation,
    )
    job = job_store.get(job_id)
    return JobResponse(job_id=job_id, module=job.module, status=job.status.value)


@router.get("/{job_id}/stream")
def stream_mulo(job_id: str) -> StreamingResponse:
    try:
        job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return sse_response(job_id)


@router.get("/{job_id}/plot-data")
def mulo_plot_data(job_id: str) -> dict:
    try:
        return get_mulo_plot_data(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
