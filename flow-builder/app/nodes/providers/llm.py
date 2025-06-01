from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.types.nodeTypes import NodeType
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType
from app.config.llms import SUPPORTED_LLMS
from app.nodes.services.llms.gpt.gpt_3_5_turbo import GPT_3_5_Turbo
from datetime import datetime
from typing import AsyncGenerator

class LLMProvider(BaseNode):
    def __init__(self, id: str, config: dict):
        self.id = id
        self.type: NodeType = "llm"
        self.config: dict = config

        super().__init__()

    def get_node_service(self):
        model = self.config.get("model")
        if not model:
            return None
        switcher: dict[SUPPORTED_LLMS, any] = {
            SUPPORTED_LLMS.GPT_3_5_TURBO: GPT_3_5_Turbo
        }
        return switcher[model]
    
    async def execute(self, data: ExecutionResultType) -> AsyncGenerator[ExecutionResultType, None]:
        node_instance = self.get_node_service()
        if not node_instance:
            yield {
                "error": "LLM model not configured",
                "errorCode": f"{self.type}/execute/model_not_configured",
                "nodeID": self.id,
                "nodeType": self.type,
                "type": "error"
            }
            return
        
        node_instance = node_instance(self.config)

        stream_data = self.config.get("streamData") == True
        content = data.get("data")
        inputText = content.get("text")
        if not inputText:
            yield {
                "error": "Input data not supported",
                "errorCode": f"{self.type}/execute/input_data_not_supported",
                "nodeID": self.id,
                "nodeType": self.type,
                "type": "error",
                "source": data.get("nodeID")
            }
            return
    
        if not stream_data:
            async for res in node_instance.execute(inputText):
                yield {
                    "data": res,
                    "nodeID": self.id,
                    "nodeType": self.type,
                    "source": data.get("nodeID")
                }
                return
        
        async for event in node_instance.execute(inputText, stream_data):
            yield {
                "nodeID": self.id,
                "data": event,
                "nodeType": self.type,
                "source": data.get("nodeID")
            }
    