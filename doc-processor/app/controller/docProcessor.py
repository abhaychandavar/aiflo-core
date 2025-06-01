from datetime import datetime
from app.services.flowService import get_node_by_id
from app.utils.db.models.knowledgebase import KnowledgeBase
from app.utils.db.models.user import Users
from bson.objectid import ObjectId
from typing import List, Optional
from app.utils.stringHelpers import generate_password
from app.utils.crypto import hash_password
from app.utils.api import APP_ERROR, StatusCode
from app.utils.jwt import create_jwt_token, create_refresh_token
from app.utils.db.models.refreshToken import RefreshTokens
from app.services.storage import Storage
from app.utils.constants import Constants
import os
import pymupdf4llm
import pymupdf
from app.types.textDocument import TextDocument
from app.services.splitter import Splitter
from app.providers.splitters.llamaIndexSplitter import LLAMAIndexSemanticSplitter
from app.services.vectorDb import VectorDb
from app.providers.vectorDb.quadrant import Quadrant
from app.services.embeddings import Embeddings
from app.providers.embeddings.openAIEmbeddings import OpenAIEmbeddings
from app.providers.embeddings.fastEmbedEmbeddings import FastEmbeddings
from app.types.splitMode import SplitMode

async def index_doc(doc_path: str, mode: str, max_characters: int):
    bucket = Constants.S3.BUCKETS.AIFLO_PUBLIC
    storage_instance = Storage()
    all_folder_keys = storage_instance.get_sorted_file_keys(bucket, doc_path)
    
    for key in all_folder_keys:
            file_name = os.path.basename(key)
            file_ext = os.path.splitext(file_name)[1].lower()
            print(f"Processing file: {key}")
            file_data = storage_instance.get_file(bucket, key)
            
            match file_ext:
                case '.pdf':
                    await index_pdf(file_data, mode, max_characters=max_characters)
                    pass
                case '.txt':
                    # process_text(file_data)
                    pass
                case '.json':
                    # process_json(file_data)
                    pass
                case _:
                    print(f"Unknown file type: {file_ext}, skipping.")

async def get_pdf_bytes_as_markdown_text(pdf_bytes: bytes) -> str:
    """
    Extracts text from a PDF file given as bytes using PyMuPDF4LLM.

    Args:
        pdf_bytes (bytes): The PDF file content as bytes.

    Returns:
        str: The extracted text from the PDF.
    """
    extracted_markdown = []
    try:
        doc = pymupdf.open(stream=pdf_bytes)
    except Exception as e:
        print(f"Error opening PDF: {e}")
        exit()
    try:
        extracted_markdown = pymupdf4llm.to_markdown(doc, page_chunks=True, force_text=True)
    except Exception as e:
        print(f"Error extracting PDF text: {e}")
        raise
    return extracted_markdown

async def index_text(text_documents: List[TextDocument], mode, max_characters):
    llama_splitter_provider = LLAMAIndexSemanticSplitter(max_characters)
    splitter = Splitter(llama_splitter_provider)
    
    splits = splitter.split(text_documents)

    quadrant_db_provider = Quadrant(os.environ['QUADRANT_NODE_URL'], os.environ['QUADRANT_API_KEY'])
    vector_db_client = VectorDb(provider=quadrant_db_provider)

    openai_embeddings_provider = OpenAIEmbeddings()
    embeddings = Embeddings(provider=openai_embeddings_provider)

    fastembed_embeddings_provider = FastEmbeddings(model_name="prithivida/Splade_PP_en_v1")
    sparse_embeddings = Embeddings(provider=fastembed_embeddings_provider)

    vector_db_dimensions = embeddings.get_dimensions()
    vector_db_client.upsert_collection(mode=mode, dense_vector_dimensions=vector_db_dimensions)

    text_docs = []
    for text_doc in splits:
        doc: TextDocument = {
            **text_doc,
            "dense_vectors": embeddings.embed(text_doc.get("text")) if mode in [SplitMode.HYBRID.value, SplitMode.SEMANTIC.value] else None,
            "sparse_vectors": sparse_embeddings.embed(text_doc.get("text")) if mode in [SplitMode.HYBRID.value, SplitMode.KEYWORDS.value] else None
        }
        text_docs.append(doc)
    
    vector_db_client.upload(text_docs, mode)

    return True

async def index_pdf(data, mode, max_characters):
    extracted_data_list = await get_pdf_bytes_as_markdown_text(data)
    print(extracted_data_list)
    extracted_docs = []
    for data in extracted_data_list:
        metadata = data.get("metadata")
        format = metadata.get("format")
        page = metadata.get("page")
        text = data.get("text")

        page_data: TextDocument = {
            "metadata": {
                "page": page,
                "format": format
            },
            "text": text
        }

        extracted_docs.append(page_data)
    
    await index_text(text_documents=extracted_docs, mode=mode, max_characters=max_characters)
    
    return True

async def _handle_process_document(body):
    flow_id = body.get("flowID")
    node_id = body.get("nodeID")

    knowledge_base = KnowledgeBase.objects(flowID=flow_id, nodeID=node_id).first()
    if not knowledge_base:
        raise APP_ERROR(code="doc-processor/not-found/knowledge-base", status_code=StatusCode.NOT_FOUND, message="Knowledge base not found")

    knowledge_base_dict = knowledge_base.to_dict()

    path = knowledge_base_dict.get("path")
    
    node = get_node_by_id(node_id=node_id, flow_id=flow_id)

    max_characters = node.get("data", {}).get("config", {}).get("max_characters", 14000)
    mode = node.get("data", {}).get("config", {}).get("mode", "semantic")

    await index_doc(
        doc_path=path,
        max_characters=max_characters,
        mode=mode
    )

    KnowledgeBase.objects(flowID=flow_id, nodeID=node_id).modify(
        __set__processedAt=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        new=True
    )

async def handle_event(message):
    body = message.get("body")
    action = message.get("action")
    switcher = {
        "process-document": _handle_process_document
    }
    await switcher[action](body=body)
    return True