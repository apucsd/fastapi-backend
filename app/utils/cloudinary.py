import re
import uuid
from pathlib import Path

import cloudinary
import cloudinary.uploader
from fastapi import UploadFile

from app.core import config


cloudinary.config(
    cloud_name=config.cloudinary_cloud_name,
    api_key=config.cloudinary_api_key,
    api_secret=config.cloudinary_api_secret,
    secure=True,
)


def generate_safe_filename(filename: str) -> str:
    name = Path(filename).stem
    extension = Path(filename).suffix.lower()

    safe_name = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        name
    ).strip("-").lower()

    unique_suffix = uuid.uuid4().hex[:6]

    return f"{safe_name}-{unique_suffix}{extension}"


async def upload_file_to_cloudinary(
    file: UploadFile,
    folder: str = "general",
) -> dict | None:
    try:
        await file.seek(0)
        file_content = await file.read()

        if not file_content:
            raise ValueError("Uploaded file is empty")

        public_id = generate_safe_filename(file.filename)

        upload_result = cloudinary.uploader.upload(
            file_content,
            folder=folder,
            resource_type="auto",
            public_id=public_id,
            overwrite=False,
        )

        return {
            "url": upload_result.get("secure_url"),
            "public_id": upload_result.get("public_id"),
            "original_filename": file.filename,
        }

    except Exception as e:
        print(f"Cloudinary upload failed: {e}")
        return None

    finally:
        await file.seek(0)