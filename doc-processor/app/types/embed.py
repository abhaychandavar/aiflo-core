from enum import Enum
from typing import List, TypedDict


class EMBED_TYPES(Enum):
    DENSE = "dense"
    SPARSE = "sparse"

class EMBED_RES(TypedDict):
    vectors: List[float]
    values: List[float]
    indices: List[int]
    type: EMBED_TYPES