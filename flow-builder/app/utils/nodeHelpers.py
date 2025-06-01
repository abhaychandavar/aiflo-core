from app.nodes.types.nodeTypes import NodeServiceExecutionResultType, ExecutionResultType

def nodeServiceOutputToProviderOutput(id: str, nodeType: str, serviceOutput: NodeServiceExecutionResultType) -> ExecutionResultType:
    return {
        'nodeID': id,
        'nodeType': nodeType,
        'data': serviceOutput
    }
