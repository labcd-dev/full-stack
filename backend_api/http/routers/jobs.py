"""Shared job and artifact routes."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from backend_api.http.config import RESULTS_DIR
from backend_api.http.schemas.common import ArtifactResponse, JobStatusResponse
from backend_api.http.services.job_store import job_store

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.get("/{job_id}", response_model=JobStatusResponse)
def get_job_status(job_id: str) -> JobStatusResponse:
    try:
        job = job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc
    return JobStatusResponse(
        job_id=job.id,
        module=job.module,
        status=job.status.value,
        metadata=job.metadata,
        error=job.error,
    )


@router.get("/{job_id}/results", response_model=ArtifactResponse)
def get_job_results(job_id: str) -> ArtifactResponse:
    try:
        job = job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    artifacts = {}
    if job.module == "trimmer":
        artifacts = job.metadata.get("artifacts", {})
    elif job.module == "recommender":
        artifacts = {"state": job.metadata}
    elif job.module == "silo":
        artifacts = {"monitor_state": job.metadata.get("monitor_state", {})}
    elif job.module == "mulo":
        artifacts = {
            "plot_data": job.metadata.get("plot_data", {}),
            "final_state": job.metadata.get("final_state"),
        }

    return ArtifactResponse(job_id=job_id, artifacts=artifacts)


@router.get("/{job_id}/artifacts/{filename}")
def download_artifact(job_id: str, filename: str):
    try:
        job_store.get(job_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Job not found") from exc

    file_path = Path(RESULTS_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Artifact not found")
    return FileResponse(path=file_path, filename=filename)
