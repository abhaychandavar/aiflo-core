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

async def generate_sequential_upload_signed_urls(space_id, file_name, count):
    id_details = get_file_ref_id(space_id=space_id, file_name=file_name)
    key = id_details["key"]

    file_essentials = generate_file_essentials(space_id=space_id, file_name=file_name, key=key)
    prefix = file_essentials["prefix"]

    storage_instance = Storage()

    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC

    signed_urls = storage_instance.generate_sequential_upload_presigned_url(
        bucket=bucket,
        count=count,
        prefix=prefix,
        file_ext=file_essentials["fileExt"]
    )

    return { "id": key, "presignedURLs": signed_urls }

async def complete_upload(space_id: str, file_name: str):
    id_details = get_file_ref_id(space_id=space_id, file_name=file_name)
    refID = id_details["id"]
    key = id_details["key"]

    file_essentials = generate_file_essentials(space_id=space_id, file_name=file_name, key=key)
    prefix = file_essentials["prefix"]
    
    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC
    storage = Storage()
    size = storage.get_folder_size(bucket=bucket, prefix=prefix)

    upserted_doc = KnowledgeBase.objects(spaceID=space_id, key=key).modify(
        set__path=prefix,
        set__uploadedAt = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        set__processedAt = None,
        set__type = KnowledgeBaseType.SEQUENTIAL,
        set__size = float(size),
        set__fileExt = file_essentials["fileExt"],
        set__fileName = file_name,
        set__refID = refID,
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
            "id": upserted_dict.get("id")
        }
    }

    comm_client.publish(message)

    return upserted_dict

def get_file_ref_id(space_id: str, file_name: str):
    id = f"{space_id}{base64.b64encode(file_name.encode("utf-8"))}"
    existing_knowledge_base = KnowledgeBase.objects(refID=id).order_by("-key").first()
    if existing_knowledge_base:
        existing_knowledge_base_dict = existing_knowledge_base.to_dict()
        return {
            "id": id,
            "isDuplicate": True,
            "key": f"{existing_knowledge_base_dict.get("key")}_copy"
        }
    return {
            "id": id,
            "isDuplicate": False,
            "key": id
        }

def generate_file_essentials(space_id: str, file_name: str, key: str):
    file_base_name = os.path.basename(file_name)
    file_ext = os.path.splitext(file_base_name)[1].lower()
    file_name = os.path.splitext(file_base_name)[0].lower()
    return {
        "prefix": f"{space_id}/{key}/{file_name}-{file_ext.split(".")[1]}",
        "fileExt": file_ext,
    }

async def get_files(space_id: str):
    files = KnowledgeBase.objects(spaceID=space_id, deletedAt=None)
    return [file.to_dict() for file in files]

def delete_document(space_id: str, key: str):
    deleted_doc = KnowledgeBase.objects(spaceID=space_id, key=key).modify(
        set__deletedAt=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        new=True
    )
    
    if not deleted_doc:
        raise APP_ERROR(
            message=f"Document with key {key} not found in space {space_id}",
            status_code=StatusCode.NOT_FOUND
        )
    
    parsed_deleted_doc = deleted_doc.to_dict()
    qstash_provider = QSTASH_PROVIDER(Settings.QSTASH_API_KEY)
    comm_client = Communications(provider=qstash_provider)

    message: MESSAGE = {
        "fromService": Settings.PROJECT_NAME,
        "toService": Settings.PROJECT_NAME,
        "type": MESSAGE_TYPE.SERVICE_TO_SERVICE.value,
        "action": "delete-document",
        "body": {
            "id": parsed_deleted_doc.get('id')
        }
    }

    comm_client.publish(message)

    return deleted_doc.to_dict()
    