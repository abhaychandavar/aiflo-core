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
import base64

async def generate_sequential_upload_signed_urls(flow_id, node_id, file_name, count):
    id_details = get_file_ref_id(flow_id=flow_id, node_id=node_id, file_name=file_name)
    id = id_details["id"]

    node = await get_node_by_id(flow_id=flow_id, node_id=node_id)
    if not node:
        raise APP_ERROR(
                status_code=StatusCode.BAD_REQUEST, 
                code="docProcessor/invalid/flow-or-node/id",
                message="Flow ID or node ID is incorrect"
            )
    
    file_essentials = generate_file_essentials(flow_id=flow_id, node_id=node_id, file_name=file_name, id=id)
    prefix = file_essentials["prefix"]

    storage_instance = Storage()

    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC

    signed_urls = storage_instance.generate_sequential_upload_presigned_url(
        bucket=bucket,
        count=count,
        prefix=prefix,
        file_ext=file_essentials["fileExt"]
    )

    return { "id": id, "presignedURLs": signed_urls }

async def complete_upload(flow_id, node_id, file_name):
    id_details = get_file_ref_id(flow_id=flow_id, node_id=node_id, file_name=file_name)
    id = id_details["id"]

    node = await get_node_by_id(flow_id=flow_id, node_id=node_id)
    if not node:
        raise APP_ERROR(
                status_code=StatusCode.BAD_REQUEST, 
                code="docProcessor/invalid/flow-or-node/id",
                message="Flow ID or node ID is is incorrect"
            )
    
    file_essentials = generate_file_essentials(flow_id=flow_id, node_id=node_id, file_name=file_name, id=id)
    prefix = file_essentials["prefix"]
    
    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC
    storage = Storage()
    size = storage.get_folder_size(bucket=bucket, prefix=prefix)

    upserted_doc = KnowledgeBase.objects(flowID=flow_id, nodeID=node_id, refID=id).modify(
        set__path=prefix,
        set__key = id_details["key"],
        set__uploadedAt = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        set__processedAt = None,
        set__type = KnowledgeBaseType.SEQUENTIAL,
        set__size = float(size),
        set__fileExt = file_essentials["fileExt"],
        set__fileName = file_name,
        upsert=True,
        new=True
    )

    qstash_provider = QSTASH_PROVIDER(Settings.QSTASH_API_KEY)
    comm_client = Communications(provider=qstash_provider)

    upserted_dict = upserted_doc.to_dict()

    message: MESSAGE = {
        "fromService": Settings.PROJECT_NAME,
        "toService": Settings.PROJECT_NAME,
        "type": MESSAGE_TYPE.SERVICE_TO_SERVICE.value,
        "action": "process-document",
        "body": {
            "id": upserted_dict.get("_id")
        }
    }

    comm_client.publish(message)

    return upserted_dict

def get_file_ref_id(flow_id: str, node_id: str, file_name: str):
    id = f"{flow_id}{node_id}{base64.b64encode(file_name.encode("utf-8"))}"
    existing_knowledge_base = KnowledgeBase.objects(key=id).order_by("-refID").first()
    if existing_knowledge_base:
        existing_knowledge_base_dict = existing_knowledge_base.to_dict()
        return {
            "id": f"{existing_knowledge_base_dict.get("refID")}_copy",
            "isDuplicate": True,
            "key": id
        }
    return {
            "id": id,
            "isDuplicate": False,
            "key": id
        }

def generate_file_essentials(flow_id: str, node_id: str, file_name: str, id: str):
    file_base_name = os.path.basename(file_name)
    file_ext = os.path.splitext(file_base_name)[1].lower()
    file_name = os.path.splitext(file_base_name)[0].lower()
    return {
        "prefix": f"{flow_id}/{node_id}/{id}/{file_name}-{file_ext.split(".")[1]}",
        "fileExt": file_ext,
    }

async def get_files(flow_id, node_id):
    files = KnowledgeBase.objects(flowID=flow_id, nodeID=node_id)
    return [file.to_dict() for file in files]