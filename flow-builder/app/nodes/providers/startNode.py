from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.types.nodeTypes import NodeType, ExecutionResultType
from app.nodes.services.start.default import DefaultStartNode
from app.nodes.interfaces.baseNodeService import Node

class StartNodeProvider(BaseNode):

    def __init__(self, id, config={}):
        self.type: NodeType = "start"

        self.id = id
        self.config = config

        super().__init__()

    def get_node_service(self) -> Node:
        if not self.config.get("text"):
            raise Exception("Input text required to process start node")
        return DefaultStartNode(self.config.get("text"))

    def execute(self, _) -> ExecutionResultType:
        node_instance = self.get_node_service()
        res = node_instance.execute()
        return {
            "nodeID": self.id,
            "data": res,
            "nodeType": self.type,
            "source": None
        }