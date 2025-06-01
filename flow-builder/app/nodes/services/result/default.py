from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeInputDataType
class DefaultResultNode(Node):
    def __init__(self, config):
        self.config = config
        super().__init__()

    def execute(self, input: str) -> ExecutionResultType:
        return input

