from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import NodeServiceExecutionResultType
from uuid import uuid4

class DefaultStartNode(Node):
    def __init__(self, input):
        self.input = input
        super().__init__()

    def execute(self, _=None) -> NodeServiceExecutionResultType:
        return {
            'id': str(uuid4()),
            'text': self.input
        }

