from fastembed import SparseTextEmbedding
from fastembed.sparse.sparse_embedding_base import SparseEmbedding
from app.types.embed import EMBED_RES, EMBED_TYPES
from app.providers.embeddings.baseEmbeddingsProvider import BaseEmbeddingsProvider
import asyncio

class FastEmbeddings(BaseEmbeddingsProvider):
    def __init__(self, model_name: str):
        self.model = SparseTextEmbedding(model_name=model_name)

    def embed(self, text: str) -> EMBED_RES:
        embed_res: EMBED_RES
        for embed in self.model.embed([text]):
            embed_as_object = embed.as_object()

            embed_res = {
                "indices": embed_as_object.get("indices"),
                "values": embed_as_object.get("values"),
                "type": EMBED_TYPES.SPARSE
            }

        return embed_res

    def get_dimensions(self) -> int:
        # FastEmbed sparse vectors are not fixed-dimension; may return None or raise NotImplementedError
        raise NotImplementedError("Sparse embeddings do not have fixed dimensions.")

    def cost_calculator(self, text: str) -> float:
        # For FastEmbed (local), cost is usually zero unless using a paid API
        return 0.0
