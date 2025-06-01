from app.types.communications import MESSAGE, MESSAGE_TYPE
from app.providers.communications.baseCommunicationsProvider import BASE_COMMUNICATIONS_PROVIDER

class Communications:
    def __init__(self, provider: BASE_COMMUNICATIONS_PROVIDER):
        self._provider = provider

    def publish(self, message: MESSAGE):
        self._provider.publish(message)
        return True