from typing import List
from app.providers.vectorDb.base import BASE_DB_PROVIDER
from app.types.textDocument import TextDocument
from app.types.splitMode import SplitMode

class VectorDb:
    def __init__(self, provider: BASE_DB_PROVIDER):
        self._provider = provider
    
    def upsert_collection(self, collection_name: str, dense_vector_dimensions):
        self._provider.upsert_collection(collection_name, dense_vector_dimensions)
        
    def upload(self, documents: List[TextDocument], collection_name: str):
        self._provider.upload(documents, collection_name)
    
    def delete_document(self, collection_name: str, space_id: str, key: str):
        self._provider.delete_document(collection_name, space_id=space_id, key=key)