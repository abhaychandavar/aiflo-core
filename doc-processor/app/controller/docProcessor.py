import datetime
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

async def index_doc(doc_path: str, max_characters: int, metadata: dict):
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
                    await index_pdf(file_data, max_characters=max_characters, additional_metadata=metadata)
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

async def index_text(text_documents: List[TextDocument], max_characters):
    collection_name = "documents"
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
    vector_db_client.upsert_collection(collection_name=collection_name, dense_vector_dimensions=vector_db_dimensions)

    from concurrent.futures import ThreadPoolExecutor
    from itertools import islice

    def process_batch(batch, embeddings, sparse_embeddings):
        batch_docs = []
        for text_doc in batch:
            doc: TextDocument = {
                **text_doc,
                "dense_vectors": embeddings.embed(text_doc.get("text")),
                "sparse_vectors": sparse_embeddings.embed(text_doc.get("text"))
            }
            batch_docs.append(doc)
        return batch_docs

    text_docs = []
    batch_size = 10  # Process 10 documents at a time

    with ThreadPoolExecutor(max_workers=4) as executor:
        # Create batches of documents
        batches = [list(islice(splits, i, i + batch_size)) 
                  for i in range(0, len(splits), batch_size)]
        
        # Process batches in parallel
        futures = [executor.submit(process_batch, batch, embeddings, sparse_embeddings) 
                  for batch in batches]
        
        # Collect results
        for future in futures:
            text_docs.extend(future.result())
    
    vector_db_client.upload(text_docs, collection_name=collection_name)

    return True

async def index_pdf(data, max_characters, additional_metadata):
    extracted_data_list = await get_pdf_bytes_as_markdown_text(data)
    extracted_docs = []
    for data in extracted_data_list:
        metadata = data.get("metadata", {})
        format = metadata.get("format")
        page = metadata.get("page")
        text = data.get("text")

        page_data: TextDocument = {
            "metadata": {
                **(additional_metadata or {}),
                "page": page,
                "format": format
            },
            "text": text
        }

        extracted_docs.append(page_data)
    
    await index_text(text_documents=extracted_docs, max_characters=max_characters)
    
    return True

async def _handle_process_document(body):
    id = body.get("id")

    knowledge_base = KnowledgeBase.objects(id=ObjectId(id)).first()
    if not knowledge_base:
        raise APP_ERROR(code="doc-processor/not-found/knowledge-base", status_code=StatusCode.NOT_FOUND, message="Knowledge base not found")

    knowledge_base_dict = knowledge_base.to_dict()

    path = knowledge_base_dict.get("path")
    
    max_characters = 1500

    await index_doc(
        doc_path=path,
        max_characters=max_characters,
        metadata={
            "spaceID": knowledge_base_dict.get("spaceID"),
            "key": knowledge_base_dict.get("key")
        }
    )

    KnowledgeBase.objects(id=ObjectId(knowledge_base_dict.get("id"))).modify(
        set__processedAt=datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None),
        new=True
    )

async def _handle_delete_document(body):
    id = body.get("id")

    knowledge_base = KnowledgeBase.objects(id=ObjectId(id)).first()
    if not knowledge_base:
        raise APP_ERROR(code="doc-processor/not-found/knowledge-base", status_code=StatusCode.NOT_FOUND, message="Knowledge base not found")
    
    knowledge_base_obj = knowledge_base.to_dict()
    quadrant_db_provider = Quadrant(os.environ['QUADRANT_NODE_URL'], os.environ['QUADRANT_API_KEY'])
    vector_db_client = VectorDb(provider=quadrant_db_provider)
    vector_db_client.delete_document(collection_name="documents", space_id=knowledge_base_obj.get("spaceID"), key=knowledge_base_obj.get("key"))
    
    KnowledgeBase.objects(id=ObjectId(id)).delete()
    
    return True

async def handle_event(message):
    body = message.get("body")
    action = message.get("action")
    switcher = {
        "process-document": _handle_process_document,
        "delete-document": _handle_delete_document
    }
    await switcher[action](body=body)
    return True  
