from abc import ABC
from app.providers.embeddings.baseEmbeddingsProvider import BaseEmbeddingsProvider
from app.types.embed import EMBED_RES

class Embeddings:
    def __init__(self, provider: BaseEmbeddingsProvider):
        if not isinstance(provider, BaseEmbeddingsProvider):
            raise TypeError("Provider must inherit from BaseEmbeddingsProvider")
        self.provider = provider

    def embed(self, text: str) -> EMBED_RES:
        return self.provider.embed(text)

    def get_dimensions(self) -> int:
        return self.provider.get_dimensions()

    def cost_calculator(self, text: str) -> float:
        return self.provider.cost_calculator(text)
