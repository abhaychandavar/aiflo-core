from abc import ABC, abstractmethod
from typing import List

class BaseEmbeddingsProvider(ABC):
    @abstractmethod
    def embed(self, text: str) -> List[float]:
        """Generate embedding vector for the input text."""
        pass

    @abstractmethod
    def get_dimensions(self) -> int:
        """Return the dimension size of the embedding vectors."""
        pass

    @abstractmethod
    def cost_calculator(self, text: str) -> float:
        """Estimate the cost in USD of generating embeddings for the given text."""
        pass
