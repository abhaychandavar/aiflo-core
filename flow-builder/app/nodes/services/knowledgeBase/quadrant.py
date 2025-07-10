from app.nodes.interfaces.baseNodeService import Node
from app.nodes.types.nodeTypes import NodeServiceExecutionResultType
from uuid import uuid4
from qdrant_client import QdrantClient, models
from app.config.knowledgeBase import Settings


class QUADRANT(Node):
    def __init__(self, top_results, query, type, generate_dense_vectors, generate_sparse_vectors, doc_ids):
        self.top_results = top_results
        self.query = query
        self.type = type
        self.generate_dense_vectors = generate_dense_vectors
        self.generate_sparse_vectors = generate_sparse_vectors
        self.client = QdrantClient(url=Settings.QUADRANT_NODE_URL, api_key=Settings.QUADRANT_API_KEY)
        self.__doc_ids = doc_ids
        
        super().__init__()

    def handle_hybrid_query(self):
        dense_vectors = self.generate_dense_vectors(self.query)
        sparse_vectors = self.generate_sparse_vectors(self.query)

        response = self.client.query_points(
            collection_name="hybrid",
            prefetch=[
                models.Prefetch(
                    query=models.SparseVector(indices=sparse_vectors["indices"], values=sparse_vectors["values"]),
                    using="text-sparse",
                    limit=self.top_results
                ),
                models.Prefetch(
                    query=dense_vectors["vectors"],
                    using="text-dense",
                    limit=self.top_results
                ),
            ],
            query=models.FusionQuery(
                fusion=models.Fusion.RRF,
            ),
            query_filter=models.Filter(
                must=[
                    models.FieldCondition(
                        key="refID",  # Updated to match the indexed field
                        match=models.MatchAny(any=self.__doc_ids)
                    )
                ]
            ),
            with_vectors=True,
            with_payload=True
        )

        res = []
        for point in response.points:
            res.append({ 
                    "id": point.id,
                    "metadata": point.payload
                })
        return res

    def handle_query(self) -> list[dict]:
        switcher = {
            "hybrid": self.handle_hybrid_query
        }

        if self.type not in switcher:
            raise ValueError(f"Unknown query type: {self.type}")

        return switcher[self.type]()

    def execute(self, _=None) -> NodeServiceExecutionResultType:
        documents = self.handle_query()
        formatted_doc_pages = []
        citations = []
        for i, doc in enumerate(documents):
            formatted_doc_pages.append(f"{doc["metadata"]["text"]} [^{i + 1}]")
            citations.append(f"[^{i + 1}]:{(doc["metadata"].get("source") and doc["metadata"]["source"] + ",") or ""} page {doc["metadata"]["page"]}")
        return {
            "id": str(uuid4()),
            "text": f"{"\n".join(formatted_doc_pages)}\n<available_citations>{"\n".join(citations)}</available_citations>",
            "dataType": "OUTPUT"
        }
