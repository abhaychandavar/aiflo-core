import datetime
import os
from app.config.default import Settings
from app.services.communications import Communications
from app.services.flowService import get_node_by_id
from app.services.storage import Storage
from app.types.communications import MESSAGE, MESSAGE_TYPE
from app.utils.api import APP_ERROR, StatusCode
from app.utils.constants import Constants
from app.utils.db.models.knowledgebase import KnowledgeBase, KnowledgeBaseType
from app.providers.communications.qstash import QSTASH_PROVIDER

async def generate_sequential_upload_signed_urls(flow_id, node_id, file_name, count):
    node = await get_node_by_id(flow_id=flow_id, node_id=node_id)
    if not node:
        raise APP_ERROR(
                status_code=StatusCode.BAD_REQUEST, 
                code="docProcessor/invalid/flow-or-node/id",
                message="Flow ID or node ID is is incorrect"
            )
    file_base_name = os.path.basename(file_name)
    file_ext = os.path.splitext(file_base_name)[1].lower()
    file_name = os.path.splitext(file_base_name)[0].lower()
    prefix = f"{flow_id}/{node_id}/{file_name}-{file_ext.split(".")[1]}"

    storage_instance = Storage()

    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC

    signed_urls = storage_instance.generate_sequential_upload_presigned_url(
        bucket=bucket,
        count=count,
        prefix=prefix,
        file_ext=file_ext
    )

    KnowledgeBase.objects(flowID=flow_id, nodeID=node_id).modify(
        set__path=prefix,
        set__uploadedAt = None,
        set__processedAt = None,
        set__type = KnowledgeBaseType.SEQUENTIAL,
        upsert=True,
        new=True
    )

    return signed_urls

async def complete_upload(flow_id, node_id):
    node = await get_node_by_id(flow_id=flow_id, node_id=node_id)
    if not node:
        raise APP_ERROR(
                status_code=StatusCode.BAD_REQUEST, 
                code="docProcessor/invalid/flow-or-node/id",
                message="Flow ID or node ID is is incorrect"
            )
    
    knowledge_base = KnowledgeBase.objects(flowID=flow_id, nodeID=node_id).first()

    if not knowledge_base:
        raise APP_ERROR(code="storage/knowledge-base/not-found", status_code=StatusCode.NOT_FOUND, message="Knowledge base not found")
    
    KnowledgeBase.objects(flowID=flow_id, nodeID=node_id).modify(
        set__uploadedAt = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        new=True
    )

    qstash_provider = QSTASH_PROVIDER(Settings.QSTASH_API_KEY)
    comm_client = Communications(provider=qstash_provider)

    message: MESSAGE = {
        "fromService": Settings.PROJECT_NAME,
        "toService": Settings.PROJECT_NAME,
        "type": MESSAGE_TYPE.SERVICE_TO_SERVICE.value,
        "action": "process-document",
        "body": {
            "flowID": flow_id,
            "nodeID": node_id
        }
    }

    comm_client.publish(message)

    return True