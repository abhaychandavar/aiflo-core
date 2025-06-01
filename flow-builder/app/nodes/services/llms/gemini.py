from time import sleep
from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import ExecutionResultType, NodeInputDataType
from typing import Generator

class GEMINI(Node):
    def __init__(self, config):
        self.config = config
        super().__init__()

    def execute(self, input: str, stream_data = False) -> Generator[str, None, None]:
        data = input + " from GEMINI akjhbhfkjsd ljdsfhkjsdnf sdjnfljasrjw snjkadfnwejknfzjbcmnsdasf a dasd ada a a a aa sdkafnasdjfb a adkbf eqagf nb"

        if not stream_data:
            yield data
            return;
    
        lastWord = ""
        for word in data.split(" "):
            print(word)
            sleep(0.5)
            lastWord = lastWord + " " +word
            yield lastWord