from typing import TypedDict
from typing_extensions import Literal, Optional


class NodeTypeEnum():
    START_NODE = 'start'
    TEXT_INPUT_NODE = 'text'
    IMAGE_INPUT_NODE = 'image'
    END_NODE = 'res'
    TEXT_OUTPUT = 'textOutput'
    IMAGE_OUTPUT = 'imageOutput'
    LLM_NODE = 'llm'
    KNOWLEDGE_BASE = 'knowledgeBase'
    FLOW = 'flow' 

NodeType = Literal["start", "res", "llm", "knowledgeBase", "textOutput", "imageOutput"]
OutputType = Literal["text"]


ExecutionResultDataType = Literal["text", "object", "error"]

class NodeInputDataType(TypedDict):
    data: dict | str
    NodeType: NodeType
    type: ExecutionResultDataType

NodeServiceExecutionResultEventType = Literal["CONTENT_PART_START", "OUTPUT", "CONTENT_PART_DONE", "PARTIAL_OUTPUT"]
class NodeServiceExecutionResultType(TypedDict):
    id: str
    text: Optional[str]
    delta: Optional[str]
    dataType: NodeServiceExecutionResultEventType
    dict: Optional[dict]
    
class ExecutionResultType(TypedDict):
    nodeID: str
    nodeType: OutputType
    data: NodeServiceExecutionResultType
    source: str
