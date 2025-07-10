import os
from qdrant_client import QdrantClient

url = os.environ['QUADRANT_NODE_URL']
api_key = os.environ['QUADRANT_API_KEY']

client = QdrantClient(url=url, api_key=api_key)

client.delete_payload_index(
    collection_name="semantic",
    field_name="refID"
)
client.create_payload_index(
    collection_name="hybrid",
    field_name="refID",
    field_schema="keyword"
)