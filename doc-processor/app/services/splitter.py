from app.providers.splitters.baseSplitter import BaseSplitter
from typing import Callable, List
from app.types.textDocument import TextDocument
from app.types.splitMode import SplitMode

class Splitter:
    def __init__(self, provider: BaseSplitter):
        self._provider = provider
    
    def split(self, documents: List[TextDocument]) -> List[TextDocument]:
        parsed_documents = self._provider.parse_documents(documents)
        return self._split_semantic(parsed_documents)
    
    def _split_semantic(self, parsed_documents: List[TextDocument]) -> List[TextDocument]:
        return self._provider.split_semantically(parsed_documents)

