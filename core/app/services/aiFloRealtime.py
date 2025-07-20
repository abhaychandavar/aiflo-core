from ably import AblyRealtime
import logging
import uuid
import json
from typing import Optional, Dict, TypedDict

class Message_Type(TypedDict):
    from_: str
    data: Dict[str, str]
    message: str
    type: str

class AIFloRealtime():
    _instance: Optional["AIFloRealtime"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AIFloRealtime, cls).__new__(cls)
            cls._instance.ably = None
        return cls._instance
    
    async def init(self, api_key: str):
        self.ably = AblyRealtime(api_key)
        await self.ably.connection.once_async('connected')
        logging.info("Connected to AIFlo realtime service")
    
    async def publish(self, channel_name: str, message: Message_Type):
        message_id = uuid.uuid4()
        channel = self.ably.channels.get(channel_name)
        message_str = json.dumps({"from": message.get("from_"), "type": message.get("type"), "message": message.get("message"), "data": message.get("data")})
        channel.publish(str(message_id), message_str)
        