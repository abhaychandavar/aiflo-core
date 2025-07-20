import openai
import tiktoken
from typing import List
from app.providers.embeddings.baseEmbeddingsProvider import BaseEmbeddingsProvider
from app.types.embed import EMBED_RES
from app.types.embed import EMBED_RES, EMBED_TYPES

class OpenAIEmbeddings(BaseEmbeddingsProvider):
    PRICING_PER_1000_TOKENS = 0.0001  # example cost in USD
    
    def __init__(self, model: str = "text-embedding-3-small", api_key: str = None):
        if api_key:
            openai.api_key = api_key
        self.model = model
        self._dimensions = None
        self.tokenizer = tiktoken.encoding_for_model(model)

    def embed(self, text: str) -> EMBED_RES:
        response = openai.embeddings.create(
            input=text,
            model=self.model
        )
        data_list = response.data
        data = data_list[0]
        embedding = data.embedding
        if self._dimensions is None:
            self._dimensions = len(embedding)
        
        res: EMBED_RES = {
            "vectors": embedding,
            "type": EMBED_TYPES.DENSE
        }
        return res

    def get_dimensions(self) -> int:
        if self._dimensions is not None:
            return self._dimensions
        embedding = self.embed("")
        return len(embedding.get("vectors"))

    def cost_calculator(self, text: str) -> float:
        tokens = self.tokenizer.encode(text)
        token_count = len(tokens)
        cost = (token_count / 1000) * self.PRICING_PER_1000_TOKENS
        return round(cost, 8)
