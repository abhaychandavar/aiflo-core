from typing import List, cast
from app.nodes.types.nodeTypes import NodeTypeEnum, NodeType
from app.nodes.node import Node
from app.nodes.interfaces.baseNodeProvider import BaseNode
from app.config.realtime import MESSAGE_TYPES
from app.config.default import Settings

import inspect

from app.nodes.providers.startNode import StartNodeProvider
from app.nodes.providers.resultNode import ResultNodeProvider
from app.nodes.providers.llm import LLMProvider

from app.services.aiFloRealtime import AIFloRealtime
from app.services.aiFloRealtime import Message_Type

class NodeBuilder:
    def __init__(self, nodes: List[dict], edges: List[dict], flow_id: str):
        self.flow_id = flow_id
        self.nodes = nodes
        self.edges = edges
        self.node_tree: Node = None

    def build(self):
        start_node, _ = self.__get_start_and_end_nodes()
        tree_root_node = Node(start_node.get("id"))
        self.node_tree = tree_root_node
        self.__build_node_tree(parent_node=tree_root_node, node=start_node)
    
    async def execute(self):
        if not self.node_tree:
            raise Exception('Build the tree by calling "build" method first.')
        async for val in self.__node_tree_executor(self.node_tree):
            yield val
    
    async def __node_tree_executor(self, node: Node, data={}):
        then_list = node.get_then()
        if inspect.iscoroutinefunction(node.exec):
            execRes = await node.exec(data)
        elif inspect.isasyncgenfunction(node.exec):
            async for execRes in node.exec(data):
                for childNode in then_list:
                    async for result in self.__node_tree_executor(childNode, execRes):
                        yield result
            return
        elif inspect.isgeneratorfunction(node.exec):
            for execRes in node.exec(data):
                for childNode in then_list:
                    async for result in self.__node_tree_executor(childNode, execRes):
                        yield result
            return
        else:
            execRes = node.exec(data)

        yield execRes

        if not then_list:
            return

        for childNode in then_list:
            async for result in self.__node_tree_executor(childNode, execRes):
                yield result

    def __build_node_tree(self, parent_node: Node, node, depth = 0):
        target_nodes = self.__get_target_nodes(node) or []
        next_node_type = None
        if len(target_nodes) == 1:
            target_node = target_nodes[0]
            next_node_type = target_node.get("type")
        
        node_exec = self.__get_node_exec(node, next_node_type == NodeTypeEnum.END_NODE)
        parent_node.set_exec_func(node_exec)
        
        for target_node in target_nodes:
            child_node = Node(target_node.get("id"))
            
            parent_node.then(child_node)
            
            self.__build_node_tree(parent_node=child_node, node=target_node, depth=depth+1)
    
    def __get_node_exec(self, node, is_next_node_output = False) -> BaseNode:
        if not node.get("id"):
            raise AttributeError("Node is missing required attribute 'id'")

        node_config = node.get("data", {}).get("config", {})
        node_config["streamData"] = node_config.get("config", {}).get("streamData") or is_next_node_output

        if not node.get('type'):
            raise AttributeError("Node is missing required attribute 'type'")
    
        type = cast(NodeType, node.get("type"))
        switcher = {
            NodeTypeEnum.START_NODE: lambda: StartNodeProvider(node.get("id"), node_config),
            NodeTypeEnum.END_NODE: lambda: ResultNodeProvider(node.get("id"), node_config),
            NodeTypeEnum.LLM_NODE: lambda: LLMProvider(node.get("id"), node_config)
        }

        return switcher[type]().execute

    def __get_start_and_end_nodes(self):
        start_node = None
        end_node = None
        for node in self.nodes:
            if node.get("type") == NodeTypeEnum.START_NODE:
                start_node = node
            elif node.get("type") == NodeTypeEnum.END_NODE:
                end_node = node
            if start_node and end_node:
                return (start_node, end_node)
        return (None, None)
    
    def __get_target_nodes(self, root_node):
        target_node_ids = []
        for edge in self.edges:
            if edge.get("target") == root_node.get("id"):
                target_node_ids.append(edge.get("source"))
        
        node_list = []

        for node in self.nodes:
            if node.get("id") in target_node_ids:
                node_list.append(node)

        return node_list
