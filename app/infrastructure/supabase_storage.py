from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

import httpx

from app.core.config import Settings
from app.core.constants import ALLOWED_IMAGE_EXTENSIONS
from app.core.exceptions import ExternalServiceException, ValidationException


@dataclass
class StoredImage:
    path: str
    public_url: str


class SupabaseStorageService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def upload_food_image(self, *, food_id: str, filename: str, content_type: str | None, content: bytes) -> StoredImage:
        extension = Path(filename).suffix.lower().lstrip(".")
        if extension not in ALLOWED_IMAGE_EXTENSIONS:
            raise ValidationException("Unsupported image format")
        if len(content) > self.settings.max_upload_size_bytes:
            raise ValidationException("Image exceeds maximum upload size")

        storage_path = f"foods/{food_id}/{uuid4().hex}.{extension}"
        upload_url = f"{self.settings.supabase_url}/storage/v1/object/{self.settings.supabase_bucket_name}/{storage_path}"
        headers = {
            "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
            "apikey": self.settings.supabase_service_role_key,
            "x-upsert": "false",
            "Content-Type": content_type or "application/octet-stream",
        }
        response = httpx.post(upload_url, headers=headers, content=content, timeout=30.0)
        if response.status_code >= 400:
            raise ExternalServiceException("Failed to upload image to Supabase Storage")
        return StoredImage(path=storage_path, public_url=self.get_public_url(storage_path))

    def delete_image(self, path: str) -> None:
        delete_url = f"{self.settings.supabase_url}/storage/v1/object/{self.settings.supabase_bucket_name}/{path}"
        headers = {
            "Authorization": f"Bearer {self.settings.supabase_service_role_key}",
            "apikey": self.settings.supabase_service_role_key,
        }
        response = httpx.delete(delete_url, headers=headers, timeout=30.0)
        if response.status_code >= 400 and response.status_code != 404:
            raise ExternalServiceException("Failed to delete image from Supabase Storage")

    def get_public_url(self, path: str) -> str:
        return f"{self.settings.supabase_url}/storage/v1/object/public/{self.settings.supabase_bucket_name}/{path}"
