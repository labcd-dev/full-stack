"""File upload routes."""

from fastapi import APIRouter, File, UploadFile

from backend_api.http.schemas.common import UploadResponse
from backend_api.http.services.regularizer_service import detect_upload_type

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("", response_model=UploadResponse)
async def upload_dynamics_file(file: UploadFile = File(...)) -> UploadResponse:
    content = (await file.read()).decode("utf-8")
    file_name, file_type = detect_upload_type(file.filename or "upload.py")
    return UploadResponse(file_name=file_name, file_type=file_type, file_content=content)
