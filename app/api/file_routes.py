from typing import List
from fastapi import APIRouter, File, UploadFile
from app.schemas.response import api_response
from app.services.file_service import FileService

router = APIRouter(prefix="/files", tags=["Files"])

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):

    image_url = await FileService.upload_file(file)
    
    if not image_url:
        return api_response(
            status_code=500,
            success=False,
            message="File upload failed",
            data=None
        )

    return api_response(
        success=True,
        message="File uploaded successfully",
        data={"url": image_url}
    )

@router.post("/upload-multiple")
async def upload_multiple_files(files: List[UploadFile] = File(...)):
    image_urls = await FileService.upload_multiple_files(files)
    
    if not image_urls:
        return api_response(
            status_code=500,
            success=False,
            message="Files upload failed",
            data=None
        )

    return api_response(
        success=True,
        message="File uploaded successfully",
        data={"url": image_urls}
    )