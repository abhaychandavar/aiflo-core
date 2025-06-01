from bson import ObjectId
from datetime import datetime

def mongo_to_dict(d):
    result = {}
    for key, value in d.items():
        if isinstance(value, dict):
            result[key] = mongo_to_dict(value)
        elif isinstance(value, list):
            result[key] = [mongo_to_dict(item) if isinstance(item, dict) else item for item in value]
        elif isinstance(value, ObjectId):
            result[key] = str(value)
        elif isinstance(value, datetime):
            result[key] = str(value)
        else:
            result[key] = value
    return result

__all__ = ["mongo_to_dict"]