import asyncio
from typing import List
from fastapi import UploadFile
from app.utils.cloudinary import upload_file_to_cloudinary

class FileService:

    @staticmethod
    async def upload_file(file: UploadFile):
        file_url = await upload_file_to_cloudinary(file)
        return file_url
    

    @staticmethod
    async def upload_multiple_files(files: List[UploadFile]):
        tasks = [upload_file_to_cloudinary(file) for file in files]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return [res for res in results if isinstance(res, str)]