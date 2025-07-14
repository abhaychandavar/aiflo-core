from concurrent.futures import ThreadPoolExecutor, as_completed
from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct, SparseVector, Distance, VectorParams, SparseVectorParams, Filter, FieldCondition, MatchValue, PointIdsList
from typing import List
from app.types.textDocument import TextDocument
from app.types.splitMode import SplitMode

class Quadrant:
    def __init__(self, url, api_key):
        self.client = QdrantClient(url=url, api_key=api_key)


    def upsert_collection(self, collection_name: str, dense_vector_dimensions):
        vectors_config = None
        sparse_config = None

        if self.client.collection_exists(collection_name=collection_name):
            print("Collection exists")
            return
        
        print("Collection does not exist, creating...")
        
        vectors_config = VectorParams(size=dense_vector_dimensions, distance=Distance.COSINE)
        sparse_config = SparseVectorParams()

        self.client.create_collection(
            collection_name=collection_name,
            vectors_config={ "text-dense": vectors_config } if vectors_config else None,
            sparse_vectors_config={
                "text-sparse": sparse_config
            } if sparse_config else None,
        )

        print(f"Collection created")

    def upload(self, documents: List[TextDocument], collection_name: str):
        def make_point(doc):
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

            return PointStruct(
                id=id,
                vector=vector,
                payload={"text": text, **metadata}
            )

        def chunkify(lst, size):
            return [lst[i:i + size] for i in range(0, len(lst), size)]

        points = [make_point(doc) for doc in documents]
        batches = chunkify(points, 20)

        def upsert_batch(batch):
            self.client.upsert(collection_name=collection_name, points=batch)
            return len(batch)

        total_uploaded = 0
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(upsert_batch, batch) for batch in batches]
            for future in as_completed(futures):
                uploaded = future.result()
                total_uploaded += uploaded

        print(f"Uploaded {total_uploaded}")
        

    def delete_document(self, collection_name: str, space_id: str, key: str):
        """
        Delete all documents in a collection that match the given key in batches of 1000.
        
        Args:
            collection_name (str): Name of the collection to delete from
            key (str): The key to match in the document payload
        """
        total_deleted = 0
        while True:
            # Get next batch of points
            points, next_offset = self.client.scroll(
                collection_name=collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(key="key", match=MatchValue(value=key)),
                        FieldCondition(key="spaceID", match=MatchValue(value=space_id)),
                    ]
                ),
                limit=1000,
                with_payload=False,
                with_vectors=False
            )
            
            if not points:
                break
                
            # Delete the batch
            self.client.delete(
                collection_name=collection_name,
                points_selector=PointIdsList(
                    points=[point.id for point in points],
                )
            )
            
            total_deleted += len(points)
            print(f"Deleted batch of {len(points)} documents with key: {key}")
            
            if not next_offset:
                break
                
        print(f"Finished deleting {total_deleted} documents with key: {key} from collection: {collection_name}")
        
