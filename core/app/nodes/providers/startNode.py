from uuid import uuid4
from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.state.nodeExecState import NodeExecState
from app.nodes.types.nodeTypes import NodeTypeEnum
from app.nodes.types.nodeTypes import NodeType, ExecutionResultType
from app.nodes.services.start.default import DefaultStartNode
from app.nodes.interfaces.baseNodeService import Node

class StartNodeProvider(BaseNode):

    def __init__(self, id, incoming_nodes: dict, config: dict, node_exec_state_instance: NodeExecState):
        self.type: NodeType = "start"

        self.id = id
        self.config = config
        self.incoming_nodes = incoming_nodes
        self.node_exec_state_instance = node_exec_state_instance

        super().__init__()

    def __get_node_service(self) -> Node:
        if not self.config.get("text"):
            raise Exception("Input text required to process start node")
        return DefaultStartNode(self.config.get("text"))

    def __execute_text_input_node(self, node):
        text = node.get("data", {}).get("config", {}).get("text")
        res: ExecutionResultType = {
            "nodeID": node.get("id"),
            "data": {
                'id': str(uuid4()),
                'text': text
            },
            "nodeType": node.get("type"),
            "source": None
        }
        self.node_exec_state_instance.set_node_exec_res(res)


    def __execute_image_input_node(self, node):
        pass

    def execute(self, _) -> ExecutionResultType:
        texts = []

        for _, node in self.incoming_nodes.items():
            if node.get("type") == NodeTypeEnum.TEXT_INPUT_NODE:
                self.__execute_text_input_node(node)
            if node.get("type") == NodeTypeEnum.IMAGE_INPUT_NODE:
                self.__execute_image_input_node(node)

        res = {
            "nodeID": self.id,
            "data": {
                'id': str(uuid4()),
                'text': "\n".join(texts)
            },
            "nodeType": self.type,
            "source": None
        }
        self.node_exec_state_instance.set_node_exec_res(res)
        return res