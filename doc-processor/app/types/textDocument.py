from typing import Optional, TypedDict, Dict, List


class TextDocument(TypedDict, total=False):
    id: str
    text: str
    dense_vectors: Optional[List[float]]
    sparse_vectors: Optional[List[float]]
    metadata: Optional[Dict[str, str]]
    relationships: Optional[Dict[str, str]]