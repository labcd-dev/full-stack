"""Regularizer API schemas."""

from typing import Optional

from pydantic import BaseModel, Field


class RegularizeRequest(BaseModel):
    file_content: str
    file_name: str = "upload"
    file_type: str = "python"
    model: str = "gpt-4o"


class RegularizeResponse(BaseModel):
    file_content: str
    change_applied: bool
    human_intervention: bool


class StandardizeRequest(BaseModel):
    file_content: str
    model: str = "gpt-4o"
    silo_pipeline: bool = False


class StandardizeResponse(BaseModel):
    file_content: str
