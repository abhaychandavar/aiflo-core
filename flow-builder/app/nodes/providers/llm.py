import re
from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.state.nodeExecState import NodeExecState
from app.nodes.types.nodeTypes import NodeType
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType
from app.config.llms import SUPPORTED_LLMS
from app.nodes.services.llms.gpt.gpt_3_5_turbo import GPT_3_5_Turbo
from datetime import datetime
from typing import AsyncGenerator
from app.nodes.utils.helpers import Helpers

class LLMProvider(BaseNode):
    def __init__(self, id: str, incoming_nodes: dict, config: dict, node_exec_state_instance: NodeExecState):
        self.id = id
        self.type: NodeType = "llm"
        self.config: dict = config
        self.incoming_nodes = incoming_nodes
        self.node_exec_state_instance = node_exec_state_instance

        super().__init__()

    def __get_node_service(self):
        model = self.config.get("model")
        if not model:
            return None
        switcher: dict[SUPPORTED_LLMS, any] = {
            SUPPORTED_LLMS.GPT_3_5_TURBO["id"]: GPT_3_5_Turbo
        }
        return switcher[model]
    
    async def execute(self, data: ExecutionResultType) -> AsyncGenerator[ExecutionResultType, None]:
        node_instance = self.__get_node_service()
        if not node_instance:
            res = {
                "error": "LLM model not configured",
                "errorCode": f"{self.type}/execute/model_not_configured",
                "nodeID": self.id,
                "nodeType": self.type,
                "type": "error"
            }
            self.node_exec_state_instance.set_node_exec_res(res)
            yield res
            return
        
        node_instance = node_instance(self.config)

        stream_data = self.config.get("streamData") == True

        raw_prompt = self.config.get("prompt")
        instructions = self.config.get("instructions")

        prompt = Helpers.hydrate_text_variables(raw_prompt, node_exec_state_instance=self.node_exec_state_instance)

        if not stream_data:
            async for res in node_instance.execute(instructions, prompt):
                res = {
                    "data": res,
                    "nodeID": self.id,
                    "nodeType": self.type,
                    "source": data.get("nodeID")
                }
                self.node_exec_state_instance.set_node_exec_res(res)
                yield res
                return
        
        async for event in node_instance.execute(instructions, prompt, stream_data):
            res = {
                "nodeID": self.id,
                "data": event,
                "nodeType": self.type,
                "source": data.get("nodeID")
            }
            self.node_exec_state_instance.set_node_exec_res(res)
            yield res
    