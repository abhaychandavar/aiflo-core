from app.nodes.types.nodeTypes import ExecutionResultType


class NodeExecState:
    def __init__(self):
        self.exec_res = {}

    def set_node_exec_res(self, res: ExecutionResultType):
        self.exec_res[res.get("nodeID")] = res

    def get_exec_res(self, node_id):
        return self.exec_res.get(node_id)
        
    def get_all_exec_res(self):
        return self.exec_res