import re
from app.nodes.state.nodeExecState import NodeExecState
from app.nodes.types.nodeTypes import ExecutionResultType

class Helpers:

    @staticmethod
    def __get_text_from_node_exec_res(exec_res: ExecutionResultType):
        text = exec_res.get("data").get("text")
        if not text: return None
        return text

    @staticmethod
    def hydrate_text_variables(text: str, node_exec_state_instance: NodeExecState) -> str:
        pattern = re.compile(r"\{(.*?)\}")

        def replacer(match):
            key = match.group(1)
            try:
                exec_res = node_exec_state_instance.get_exec_res(key)
                value = Helpers.__get_text_from_node_exec_res(exec_res)
                return str(value) if value is not None else ""
            except Exception as e:
                return f"{{{key}}}"

        return pattern.sub(replacer, text)