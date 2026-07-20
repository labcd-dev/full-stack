"""Admin image uploads for site branding and blog covers."""

from __future__ import annotations

import uuid

from fastapi import UploadFile

from backend_api.http.config import API_PREFIX, UPLOADS_DIR

MEDIA_DIR = UPLOADS_DIR / "media"
ALLOWED_IMAGE_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/gif": ".gif",
    "image/svg+xml": ".svg",
}
MAX_IMAGE_BYTES = 5 * 1024 * 1024


async def save_admin_image(file: UploadFile, *, prefix: str = "image") -> str:
    content_type = (file.content_type or "").lower()
    extension = ALLOWED_IMAGE_TYPES.get(content_type)
    if extension is None:
        raise ValueError("Image must be JPEG, PNG, WebP, GIF, or SVG")

    data = await file.read()
    if not data:
        raise ValueError("Image file is empty")
    if len(data) > MAX_IMAGE_BYTES:
        raise ValueError("Image must be 5 MB or smaller")

    MEDIA_DIR.mkdir(parents=True, exist_ok=True)
    safe_prefix = "".join(ch if ch.isalnum() or ch in "-_" else "-" for ch in prefix)[:32] or "image"
    filename = f"{safe_prefix}-{uuid.uuid4().hex[:12]}{extension}"
    path = MEDIA_DIR / filename
    path.write_bytes(data)
    return f"{API_PREFIX}/uploads/media/{filename}"
