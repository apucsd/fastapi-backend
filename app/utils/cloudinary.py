import cloudinary
import cloudinary.uploader
from app.core import config
from fastapi import UploadFile

cloudinary.config(
    cloud_name=config.cloudinary_cloud_name,
    api_key=config.cloudinary_api_key,
    api_secret=config.cloudinary_api_secret,
    secure=True
)

async def upload_file_to_cloudinary(file: UploadFile, folder: str = "general"):
    try:
        file_content = await file.read()
        
        upload_result = cloudinary.uploader.upload(
            file_content, 
            folder=folder,
            resource_type="auto"
        )
        
        return upload_result.get("secure_url")
    except Exception as e:
        print(f"File upload error: {e}")
        return None
    finally:
        await file.seek(0)
