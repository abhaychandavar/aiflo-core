import os
from typing import TypedDict

class KNOWLEDGE_BASE():
    QUADRANT = {
            "id": "quadrant",
            "name": "Quadrant"
        }

    @classmethod
    def get_db_dict(cls):
        dbs = {}
        for attr_name in dir(cls):
            if not attr_name.startswith('_') and not callable(getattr(cls, attr_name)):
                attr_value = getattr(cls, attr_name)
                if isinstance(attr_value, dict) and 'id' in attr_value and 'name' in attr_value:
                    dbs[attr_name] = attr_value
        return dbs

class Settings:
    QUADRANT_NODE_URL=os.getenv("QUADRANT_NODE_URL")
    QUADRANT_API_KEY=os.getenv("QUADRANT_API_KEY")