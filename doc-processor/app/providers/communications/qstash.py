from qstash import QStash
from app.types.communications import MESSAGE, MESSAGE_TYPE
from app.config.default import Settings
from app.utils.api import APP_ERROR, StatusCode
from app.providers.communications.baseCommunicationsProvider import BASE_COMMUNICATIONS_PROVIDER

class QSTASH_PROVIDER(BASE_COMMUNICATIONS_PROVIDER):
    def __init__(self, api_key: str):
        self._client = QStash(api_key, base_url="https://qstash.upstash.io")
        
    def _publish_service_to_service(self, message: MESSAGE):
        service_event_url = Settings.SERVICES.get("doc-processor", {}).get("event-url", None)
        if not service_event_url:
            raise APP_ERROR(
                code="qstash/communications/invalid/service",
                message="Invalid \"to\" address",
                status_code=StatusCode.BAD_REQUEST
            )
        self._client.message.publish_json(
            url=service_event_url,
            body=message,
        )

    def publish(self, message: MESSAGE) -> bool:
        type = message["type"]
        switcher = {
            MESSAGE_TYPE.SERVICE_TO_SERVICE.value: self._publish_service_to_service
        }
        method = switcher[type]
        if not method:
            raise APP_ERROR(status_code=StatusCode.BAD_REQUEST, code="communications/invalid/message-type", message=f"Invalid message type, supported types are: {switcher.keys()}")
        method(message)
        return True