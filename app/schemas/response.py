from typing import Any
from fastapi.responses import JSONResponse
def api_response(status_code: int = 200, success: bool = True, message: str = "No message from server", meta: Any = None, data: Any = None):
    content = {
        "status_code": status_code,
        "success": success,
        "message": message,
    }

    if meta is not None:
        content["meta"] = meta

    content["data"] = data

    return JSONResponse(status_code=status_code, content=content)