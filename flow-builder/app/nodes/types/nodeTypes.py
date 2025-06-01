from typing import TypedDict
from typing_extensions import Literal, Optional


class NodeTypeEnum():
    START_NODE = 'start'
    END_NODE = 'res'
    LLM_NODE = 'llm'

NodeType = Literal["start", "res", "llm"]
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
    
class ExecutionResultType(TypedDict):
    nodeID: str
    nodeType: OutputType
    data: NodeServiceExecutionResultType
    source: str
