from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SparseVector, Distance, VectorParams, SparseVectorParams
from typing import List
from app.types.textDocument import TextDocument
from app.types.splitMode import SplitMode

class Quadrant:
    def __init__(self, url, api_key):
        self.client = QdrantClient(url=url, api_key=api_key)


    def upsert_collection(self, mode: SplitMode, dense_vector_dimensions):
        vectors_config = None
        sparse_config = None

        if self.client.collection_exists(mode):
                print("Collection exists")
                return
        print("Collection does not exist, creating...")
        
        if mode == SplitMode.SEMANTIC.value:
            vectors_config = VectorParams(size=dense_vector_dimensions, distance=Distance.COSINE)  # Adjust size to match your embedding model
        elif mode == SplitMode.KEYWORDS.value:
            sparse_config = SparseVectorParams()
        elif mode == SplitMode.HYBRID.value:
            vectors_config = VectorParams(size=dense_vector_dimensions, distance=Distance.COSINE)
            sparse_config = SparseVectorParams()

        self.client.create_collection(
            collection_name=mode,
            vectors_config={ "text-dense": vectors_config } if vectors_config else None,
            sparse_vectors_config={
                "text-sparse": sparse_config
            } if sparse_config else None,
        )

        print(f"Collection created")

    def upload(self, documents: List[TextDocument], mode: SplitMode):
        points = []
        for doc in documents:
            dense_vectors = doc.get("dense_vectors")
            sparse_vectors = doc.get("sparse_vectors")
            text = doc.get("text")
            metadata = doc.get("metadata")
            id = doc.get("id")

            vector = {}

            if sparse_vectors:
                vector["text-sparse"] = SparseVector(
                            indices=sparse_vectors["indices"],
                            values=sparse_vectors["values"]
                        )
            if dense_vectors:
                vector["text-dense"] = dense_vectors.get("vectors")

            point = PointStruct(
                id=id,
                vector=vector,
                payload={"text": text, **metadata}
            )
            
            points.append(point)

            if len(points) >= 50:
                self.client.upsert(collection_name=mode, points=points)
                points = []

        if len(points):
            self.client.upsert(collection_name=mode, points=points)
        
        print(f"Uploaded {len(points)}")
        
