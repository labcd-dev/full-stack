"""Pydantic schemas for blog CMS."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class BlogPostOut(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    body_markdown: str
    cover_image_url: str | None
    status: str
    published_at: datetime | None
    author_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlogPostListItem(BaseModel):
    id: int
    title: str
    slug: str
    excerpt: str
    cover_image_url: str | None
    status: str
    published_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BlogPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=300)
    slug: str | None = Field(None, max_length=320)
    excerpt: str = ""
    body_markdown: str = ""
    cover_image_url: str | None = Field(None, max_length=512)
    status: str = Field("draft", pattern="^(draft|published)$")


class BlogPostUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=300)
    slug: str | None = Field(None, min_length=1, max_length=320)
    excerpt: str | None = None
    body_markdown: str | None = None
    cover_image_url: str | None = Field(None, max_length=512)
    status: str | None = Field(None, pattern="^(draft|published)$")
