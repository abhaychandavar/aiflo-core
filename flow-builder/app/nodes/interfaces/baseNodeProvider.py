from abc import abstractmethod


from abc import ABC, abstractmethod
from typing import TypedDict
from app.nodes.types.nodeTypes import ExecutionResultType

class BaseNode(ABC):
    @abstractmethod
    def execute(self, data) -> ExecutionResultType:
        pass
