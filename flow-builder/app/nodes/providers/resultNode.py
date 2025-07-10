from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.state.nodeExecState import NodeExecState
from app.nodes.types.nodeTypes import NodeType
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType

class ResultNodeProvider(BaseNode):
    def __init__(self, id: str, incoming_nodes: dict, config: dict, node_exec_state_instance: NodeExecState):
        self.type: NodeType = "res"
        self.id = id
        self.config = config
        self.incoming_nodes = incoming_nodes
        self.node_exec_state_instance = node_exec_state_instance

        super().__init__()

    def __get_node_service(self) -> Node:
        return DefaultResultNode(self.config)

    def execute(self, data: ExecutionResultType) -> ExecutionResultType:
        node_instance = self.__get_node_service()
        content = data.get("data")
        res = node_instance.execute(content)
        res = {
            "nodeID": self.id,
            "data": res,
            "nodeType": self.type,
            "source": data.get("nodeID")
        }
        self.node_exec_state_instance.set_node_exec_res(res)
        return res