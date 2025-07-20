from abc import abstractmethod
from app.nodes.types.nodeTypes import NodeServiceExecutionResultType
    
class Node():
    @abstractmethod
    def execute(self) -> NodeServiceExecutionResultType :
        pass