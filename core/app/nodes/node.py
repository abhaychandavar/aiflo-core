from collections.abc import Awaitable
from typing import Callable, List, Dict, Union

DictFunction = Union[
    Callable[[], Dict],                  # Sync function returning dict
    Callable[[], Awaitable[Dict]]       # Async function returning dict
]

class Node:
    def __init__(self, id: str, type: str):
        self.id = id
        self.__then: List['Node'] = []
        self.exec: DictFunction
        self.type = type

    def print(self):
        self.__print(self, depth=0)
    
    def __print(self, node, depth=0):
        print(f"{"-"*depth}{node.id}")
        then_list = node.get_then()
        for curr_node in then_list:
            self.__print(curr_node, depth=depth+1)
    
    def set_exec_func(self, func: Callable[[Dict], Dict]):
        self.exec = func

    def then(self, *nodes: 'Node'):
        self.__then.extend(nodes)

    def get_then(self):
        return self.__then
    