from typing import List
from app.providers.vectorDb.base import BASE_DB_PROVIDER
from app.types.textDocument import TextDocument
from app.types.splitMode import SplitMode

class VectorDb:
    def __init__(self, provider: BASE_DB_PROVIDER):
        self._provider = provider
    
    def upsert_collection(self, mode: SplitMode, dense_vector_dimensions):
        self._provider.upsert_collection(mode, dense_vector_dimensions)
        
    def upload(self, documents: List[TextDocument], mode: SplitMode):
        self._provider.upload(documents, mode)