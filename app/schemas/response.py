from typing import Any
from datetime import datetime, date
from uuid import UUID
from fastapi.responses import JSONResponse
import json
import enum

EXCLUDE_FIELDS = {"password", "otp", "otp_expiry"}


class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        if isinstance(obj, UUID):
            return str(obj)
        if isinstance(obj, enum.Enum):
            return obj.value
        return super().default(obj)


def serialize(data: Any) -> Any:
    if isinstance(data, list):
        return [serialize(item) for item in data]
    elif isinstance(data, dict):
        return {k: serialize(v) for k, v in data.items()}
    elif isinstance(data, (datetime, date)):
        return data.isoformat()
    elif isinstance(data, UUID):
        return str(data)
    elif isinstance(data, enum.Enum):
        return data.value
    elif hasattr(data, "__dict__"):
        return {
            k: serialize(v)
            for k, v in data.__dict__.items()
            if not k.startswith("_") and k not in EXCLUDE_FIELDS
        }
    return data


def api_response(
    status_code: int = 200,
    success: bool = True,
    message: str = "No message from server",
    meta: Any = None,
    data: Any = None,
):
    content = {
        "status_code": status_code,
        "success": success,
        "message": message,
    }

    if meta is not None:
        content["meta"] = meta

    content["data"] = serialize(data)

    return JSONResponse(
        status_code=status_code,
        content=json.loads(json.dumps(content, cls=CustomEncoder)),
    )
