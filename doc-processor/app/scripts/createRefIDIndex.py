from dotenv import load_dotenv
load_dotenv()

import os
from qdrant_client import QdrantClient

url = os.environ['QUADRANT_NODE_URL']
api_key = os.environ['QUADRANT_API_KEY']

client = QdrantClient(url=url, api_key=api_key)
print("creating indices")
client.create_payload_index(
    collection_name="documents",
    field_name="key",
    field_schema="keyword"
)

client.create_payload_index(
    collection_name="documents",
    field_name="spaceID",
    field_schema="keyword"
)
print("Indices created")