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
from app.nodes.providers.knowledgeBase import KnowledgeBase
from app.nodes.providers.flow import Flow

from app.services.aiFloRealtime import AIFloRealtime
from app.services.aiFloRealtime import Message_Type

from app.nodes.state.nodeExecState import NodeExecState

class NodeBuilder:
    def __init__(self, nodes: List[dict], edges: List[dict], flow_id: str, space_id: str):
        self.flow_id = flow_id
        self.nodes = nodes
        self.edges = edges
        self.node_tree: Node = None
        self.__space_id = space_id
    
    def get_incoming_nodes(self, node, incoming_nodes=None, nodes_map=None, seen_nodes=None):
        """
        Get all incoming nodes (nodes that this node connects to) recursively.
        
        Args:
            node: The starting node
            incoming_nodes: List to accumulate incoming nodes (mutable default avoided)
            nodes_map: Dictionary mapping node IDs to nodes for fast lookup
            seen_nodes: Set of already processed node IDs to avoid cycles
        
        Returns:
            List of incoming nodes
        """

        if incoming_nodes is None:
            incoming_nodes = {}
        if nodes_map is None:
            nodes_map = {'nodes': {}, 'size': 0}
        if seen_nodes is None:
            seen_nodes = set()
        
        if not nodes_map['size']:
            for n in self.nodes:
                nodes_map['nodes'][n["id"]] = n
                nodes_map['size'] += 1
        
        immediate_incoming_node_ids = [
            edge["target"] for edge in self.edges 
            if edge["source"] == node["id"]
        ]
        
        for node_id in immediate_incoming_node_ids:
            if node_id in seen_nodes:
                continue
            
            target_node = nodes_map['nodes'][node_id]
            incoming_nodes[target_node["id"]] = target_node
            
            self.get_incoming_nodes(
                    node=target_node, 
                    incoming_nodes=incoming_nodes, 
                    nodes_map=nodes_map, 
                    seen_nodes=seen_nodes
                )
            seen_nodes.add(node_id)
        
        return incoming_nodes

    def build(self):
        start_node, _ = self.__get_start_and_end_nodes()
        tree_root_node = Node(start_node.get("id"), start_node.get("type"))
        self.node_tree = tree_root_node
        node_exec_state = NodeExecState()
        self.__build_node_tree(parent_node=tree_root_node, node=start_node, node_exec_state=node_exec_state, space_id=self.__space_id, flow_id=self.flow_id)
    
    async def execute(self, only_result=False):
        node_state = NodeExecState()
        if not self.node_tree:
            raise Exception('Build the tree by calling "build" method first.')
        async for val in self.__node_tree_executor(node=self.node_tree, node_state=node_state, only_result=only_result):
            yield val

    async def __node_tree_executor(
        self,
        node: Node,
        node_state: NodeExecState,
        data=None,
        *,
        only_result: bool = False,
    ):
        """
        Depth-first async traversal of a node tree.

        Parameters
        ----------
        node : Node
            Current node to execute.
        node_state : NodeExecState
            Execution state (not shown; presumably holds context).
        data : Any, optional
            Input payload passed to `node.exec`. Defaults to {} (changed to None in signature
            to avoid the mutable-default trap; see below).
        only_result : bool, default False
            - False: yield every node's execution result (original behavior).
            - True: yield **only leaf node** results (nodes with no `then` children).

        Yields
        ------
        Any
            Execution results from nodes per `only_result` rule.
        """
        if data is None:
            data = {}

        then_list = node.get_then()
        has_children = bool(then_list)

        # Helper to recurse into children
        async def _recurse_children(execRes):
            for childNode in then_list:
                async for result in self.__node_tree_executor(
                    childNode, node_state, execRes, only_result=only_result
                ):
                    yield result

        # -- CASES: coroutine, async-gen, sync-gen, sync callable -----------------
        if inspect.iscoroutinefunction(node.exec):
            execRes = await node.exec(data)

            # Yield current node result only if not suppressing intermediates
            if (not only_result) or (not has_children):
                yield execRes

            if has_children:
                async for r in _recurse_children(execRes):
                    yield r
            return

        elif inspect.isasyncgenfunction(node.exec):
            async for execRes in node.exec(data):
                # Same suppression rule applies to each produced value
                if (not only_result) or (not has_children):
                    yield execRes

                if has_children:
                    async for r in _recurse_children(execRes):
                        yield r
            return

        elif inspect.isgeneratorfunction(node.exec):
            for execRes in node.exec(data):
                if (not only_result) or (not has_children):
                    yield execRes

                if has_children:
                    async for r in _recurse_children(execRes):
                        yield r
            return

        else:
            execRes = node.exec(data)

            if (not only_result) or (not has_children):
                yield execRes

            if has_children:
                async for r in _recurse_children(execRes):
                    yield r
            return


    def __build_node_tree(self, parent_node: Node, node, node_exec_state, space_id: str, flow_id: str, depth = 0):
        target_nodes = (self.__get_target_nodes(node) or []) if node.get("type") != NodeTypeEnum.END_NODE else []
        next_node_type = None
        if len(target_nodes) == 1:
            target_node = target_nodes[0]
            next_node_type = target_node.get("type")
        
        incoming_nodes = self.get_incoming_nodes(
            node=node,
        )

        node_exec = self.__get_node_exec(
            node=node, 
            is_next_node_output=next_node_type == NodeTypeEnum.END_NODE, 
            incoming_nodes=incoming_nodes,
            node_exec_state_instance=node_exec_state,
            space_id=space_id
        )
        parent_node.set_exec_func(node_exec)
        
        for target_node in target_nodes:
            child_node = Node(target_node.get("id"), target_node.get("type"))
            
            parent_node.then(child_node)
            
            self.__build_node_tree(parent_node=child_node, node=target_node, node_exec_state=node_exec_state, space_id=space_id, flow_id=flow_id, depth=depth+1)
    
    def __get_node_exec(self, node, is_next_node_output, incoming_nodes: dict, node_exec_state_instance: NodeExecState, space_id: str) -> BaseNode:
        if not node.get("id"):
            raise AttributeError("Node is missing required attribute 'id'")

        node_config = node.get("data", {}).get("config", {})
        node_config["isDataStreamingAllowed"] = is_next_node_output or False
        node_config["spaceID"] = space_id

        if not node.get('type'):
            raise AttributeError("Node is missing required attribute 'type'")
    
        type = cast(NodeType, node.get("type"))
        switcher = {
            NodeTypeEnum.START_NODE: lambda: StartNodeProvider(
                id=node.get("id"), 
                config=node_config,
                incoming_nodes=incoming_nodes,
                node_exec_state_instance=node_exec_state_instance
            ),
            NodeTypeEnum.END_NODE: lambda: ResultNodeProvider(
                id=node.get("id"), 
                config=node_config,
                incoming_nodes=incoming_nodes,
                node_exec_state_instance=node_exec_state_instance
            ),
            NodeTypeEnum.LLM_NODE: lambda: LLMProvider(
                id=node.get("id"), 
                config=node_config,
                incoming_nodes=incoming_nodes,
                node_exec_state_instance=node_exec_state_instance
            ),
            NodeTypeEnum.KNOWLEDGE_BASE: lambda: KnowledgeBase(
                id=node.get("id"), 
                config=node_config,
                incoming_nodes=incoming_nodes,
                node_exec_state_instance=node_exec_state_instance
            ),
            NodeTypeEnum.FLOW: lambda: Flow(
                id=node.get("id"), 
                config=node_config,
                incoming_nodes=incoming_nodes,
                node_exec_state_instance=node_exec_state_instance,
                space_id=self.__space_id,
                flow_id=self.flow_id,
                node_core=NodeBuilder
            ),
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
