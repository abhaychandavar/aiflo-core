from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.types.nodeTypes import NodeType
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType

class ResultNodeProvider(BaseNode):
    def __init__(self, id, config={}):
        self.type: NodeType = "res"

        self.id = id
        self.config = config

        super().__init__()

    def get_node_service(self) -> Node:
        return DefaultResultNode(self.config)

    def execute(self, data: ExecutionResultType) -> ExecutionResultType:
        node_instance = self.get_node_service()
        content = data.get("data")
        res = node_instance.execute(content)
        return {
            "nodeID": self.id,
            "data": res,
            "nodeType": self.type,
            "source": data.get("nodeID")
        }