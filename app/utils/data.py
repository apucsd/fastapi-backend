from typing import Any, Dict, Union
from pydantic import BaseModel


def get_update_data(data: Union[Dict[str, Any], BaseModel, Any]) -> Dict[str, Any]:
    """
    Translates any input (Dict, Pydantic, or SQLAlchemy object)
    into a clean dictionary of fields to update,
    equivalent to how req.body works in Express.
    """
    if isinstance(data, dict):
        return data

    # Handle Pydantic V2
    if hasattr(data, "model_dump"):
        return data.model_dump(exclude_unset=True)

    # Handle Pydantic V1
    if hasattr(data, "dict"):
        return data.dict(exclude_unset=True)

    # Handle SQLAlchemy or other objects
    if hasattr(data, "__table__"):
        return {
            c.name: getattr(data, c.name)
            for c in data.__table__.columns
            if not c.primary_key
        }

    return vars(data)
