import re
from uuid import uuid4
from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.nodes.state.nodeExecState import NodeExecState
from app.nodes.types.nodeTypes import NodeType, NodeTypeEnum
from app.nodes.services.result.default import DefaultResultNode
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeServiceExecutionResultType
from app.config.llms import SUPPORTED_LLMS
from app.nodes.services.llms.gpt.gpt_3_5_turbo import GPT_3_5_Turbo
from datetime import datetime
from typing import AsyncGenerator
from app.nodes.utils.helpers import Helpers
import requests
from app.config.default import Settings
from app.utils.flow import get_flow_by_id

class Flow(BaseNode):
    def __init__(self, id: str, incoming_nodes: dict, config: dict, node_exec_state_instance: NodeExecState, space_id: str, flow_id: str, node_core):
        self.id = id
        self.type: NodeType = "flow"
        self.config: dict = config
        self.incoming_nodes = incoming_nodes
        self.node_exec_state_instance = node_exec_state_instance
        self.__flow_id = flow_id
        self.__space_id = space_id
        self.__node_core = node_core

        super().__init__()
    
    def get_flow(self, flow_id: str):
        flow_data = get_flow_by_id(flow_id)
        return flow_data.get("flow")
    
    def get_input_nodes_and_index(self, nodes, edges):
        start_node_id = None
        for node in nodes:
            if node.get("type") == NodeTypeEnum.START_NODE:
                start_node_id = node.get("id")
                break
        
        if not start_node_id:
            return None
        
        inp_node_ids = []
        for edge in edges:
            if edge.get("source") == start_node_id:
                inp_node_ids.append(edge.get("target"))
        
        inp_nodes = []
        for idx, node in enumerate(nodes):
            if node.get("id") in inp_node_ids:
                inp_nodes.append({
                    "idx": idx,
                    "type": node.get("type")
                })
        return inp_nodes

    def update_nodes_input(self, nodes, edges, text):
        nodes_list = nodes
        nodes_map = {}

        for node in nodes_list:
            nodes_map[node.get("id")] = node
        
        input_node_list = self.get_input_nodes_and_index(nodes_list, edges)
        
        for node in input_node_list:
            if node.get("type") == "text":
                idx = node.get("idx")
                nodes_list[idx] = {
                    **nodes_list[idx],
                    "data": {
                        **(nodes_list[idx].get("data", {})),
                        "config": {
                            **(nodes_list[idx].get("data", {}).get("config", {})),
                            "text": text
                        }
                    }
                }
        
        return nodes_list

    async def execute(self, data: ExecutionResultType) -> AsyncGenerator[ExecutionResultType, None]:
        flow_id = self.config.get("flowID")
        flow = self.get_flow(flow_id)
        
        nodes = flow.get("nodes")
        input_data = data.get("data")
        text = input_data.get("text")

        edges = flow.get("edges")
        nodes = self.update_nodes_input(nodes=nodes, edges=edges, text=text)

        node_builder = self.__node_core(
            nodes=nodes,
            edges=edges,
            flow_id=self.__flow_id,
            space_id=self.__space_id
        )
        node_builder.build()

        stream_data = self.config.get("isDataStreamingAllowed") is True

        if stream_data:
            async for exec_res in node_builder.execute(only_result=True):
                if not isinstance(exec_res, dict):
                    raise TypeError(f"Expected exec_res to be dict, got {type(exec_res)}")

                message_id = str(uuid4())
                payload = {
                    "nodeID": self.id,
                    "data": exec_res.get("data"),
                    "nodeType": self.type,
                    "source": data.get("nodeID"),
                    "eventID": message_id
                }

                self.node_exec_state_instance.set_node_exec_res(payload)
                yield payload
            return

        final_exec_res: ExecutionResultType = None
        async for exec_res in node_builder.execute(only_result=True):
            if not isinstance(exec_res, dict):
                raise TypeError(f"Expected exec_res to be dict, got {type(exec_res)}")
            final_exec_res = exec_res

        if final_exec_res is None:
            raise RuntimeError("No result produced by node execution")

        res = {
            "nodeID": self.id,
            "data": final_exec_res.get("data"),
            "nodeType": self.type,
            "source": data.get("nodeID")
        }
        self.node_exec_state_instance.set_node_exec_res(res)
        yield res


    