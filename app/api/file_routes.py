from typing import Dict, List
from fastapi import APIRouter, File, UploadFile, status

from app.schemas.response import ApiResponse
from app.services.file_service import FileService
from app.utils.exceptions import AppException

router = APIRouter(prefix="/files", tags=["Files"])


@router.post(
    "/upload",
    response_model=ApiResponse[Dict[str, str]],
    status_code=status.HTTP_201_CREATED,
)
async def upload_file(file: UploadFile = File(...)):
    image_url = await FileService.upload_file(file)
    if not image_url:
        raise AppException(
            status_code=500, message="File upload failed"
        )

    return ApiResponse(
        message="File uploaded successfully",
        data={"url": image_url},
    )


@router.post(
    "/upload-multiple",
    response_model=ApiResponse[Dict[str, List[str]]],
    status_code=status.HTTP_201_CREATED,
)
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    image_urls = await FileService.upload_multiple_files(files)
    if not image_urls:
        raise AppException(
            status_code=500, message="Files upload failed"
        )

    return ApiResponse(
        message="Files uploaded successfully",
        data={"url": image_urls},
    )