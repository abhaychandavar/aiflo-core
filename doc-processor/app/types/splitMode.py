from ast import List
from enum import Enum
from typing import Literal

class SplitMode(Enum):
    SEMANTIC = "semantic"
    KEYWORDS = "keywords"
    HYBRID   = "hybrid"