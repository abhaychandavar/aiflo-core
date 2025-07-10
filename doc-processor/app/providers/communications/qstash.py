import threading
import requests
from qstash import QStash
from app.types.communications import MESSAGE, MESSAGE_TYPE
from app.config.default import Settings
from app.utils.api import APP_ERROR, StatusCode
from app.providers.communications.baseCommunicationsProvider import BASE_COMMUNICATIONS_PROVIDER

class QSTASH_PROVIDER(BASE_COMMUNICATIONS_PROVIDER):
    def __init__(self, api_key: str):
        self._client = QStash(api_key, base_url="https://qstash.upstash.io")

    def __fire_and_forget(self, url, message):
        try:
            requests.post(url, json=message, timeout=2)  # optional timeout
        except Exception as e:
            # Log the error, but don’t raise it — it's fire-and-forget
            print(f"Background request failed: {e}")

    def _publish_service_to_service(self, message: MESSAGE):
        service_event_url = Settings.SERVICES.get("doc-processor", {}).get("event-url", None)
        if not service_event_url:
            raise APP_ERROR(
                code="qstash/communications/invalid/service",
                message="Invalid \"to\" address",
                status_code=StatusCode.BAD_REQUEST
            )
        if Settings.ENV != "local":
            self._client.message.publish_json(
                url=service_event_url,
                body=message,
            )
        else:
            try:
                threading.Thread(
                    target=self.__fire_and_forget,
                    args=(service_event_url, message),
                    daemon=True
                ).start()
            except (Exception) as e:
                raise APP_ERROR(
                    code="qstash/local/request-failed",
                    message=f"Local API call failed: {str(e)}",
                    status_code=StatusCode.SOMETHING_WENT_WRONG
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