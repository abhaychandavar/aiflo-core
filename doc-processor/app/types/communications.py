from typing import TypedDict
from enum import Enum

class MESSAGE_TYPE(str, Enum):
    SERVICE_TO_SERVICE = "service-to-service"


class MESSAGE(TypedDict):
    fromService: str
    toService: str
    body: dict[str, str]
    type: MESSAGE_TYPE
    action: str