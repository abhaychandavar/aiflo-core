from bson import ObjectId
from datetime import datetime
from mongoengine import Document
from enum import Enum

def mongo_to_dict(d, ignore_fields=["password"]):
    result = {}
    for key in d._fields:
        value = getattr(d, key)

        if key in ignore_fields:
            continue

        if isinstance(value, Document):
            result[key] = mongo_to_dict(value)  # handle ReferenceFields
        elif isinstance(value, list):
            result[key] = [mongo_to_dict(v) if isinstance(v, Document) else v for v in value]
        elif isinstance(value, dict):
            result[key] = {
                k: mongo_to_dict(v) if isinstance(v, Document) else v
                for k, v in value.items()
            }
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = value.isoformat()
        elif isinstance(value, Enum):
            result[key] = value.value
        else:
            result[key] = value
    return result

__all__ = ["mongo_to_dict"]