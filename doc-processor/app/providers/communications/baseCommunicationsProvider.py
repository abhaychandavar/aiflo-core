from abc import ABC, abstractmethod
from app.types.communications import MESSAGE

class BASE_COMMUNICATIONS_PROVIDER:
    @abstractmethod
    def publish(message: MESSAGE) -> bool: pass