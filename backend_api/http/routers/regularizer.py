"""Regularizer routes."""

from fastapi import APIRouter

from backend_api.http.schemas.regularizer import (
    RegularizeRequest,
    RegularizeResponse,
    StandardizeRequest,
    StandardizeResponse,
)
from backend_api.http.services.regularizer_service import run_regularize, run_standardize

router = APIRouter(prefix="/regularize", tags=["regularizer"])


@router.post("", response_model=RegularizeResponse)
def regularize_file(request: RegularizeRequest) -> RegularizeResponse:
    result = run_regularize(
        request.file_content,
        request.file_name,
        request.file_type,
        request.model,
    )
    return RegularizeResponse(
        file_content=result["file_content"],
        change_applied=result["change_applied"],
        human_intervention=result["human_intervention"],
    )


@router.post("/standardize", response_model=StandardizeResponse)
def standardize_file(request: StandardizeRequest) -> StandardizeResponse:
    result = run_standardize(request.file_content, request.model, request.silo_pipeline)
    return StandardizeResponse(file_content=result["file_content"])
