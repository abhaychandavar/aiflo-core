import logging
from app.utils.db.models.user import Users
from bson.objectid import ObjectId
from typing import Optional
from app.utils.stringHelpers import generate_password
from app.utils.crypto import hash_password
from app.utils.api import APP_ERROR, StatusCode
from app.utils.jwt import create_jwt_token, create_refresh_token
from app.utils.db.models.refreshToken import RefreshTokens

import boto3

s3 = boto3.client('s3')

async def index_doc(doc_path: str):
    pass

def stream_text_lines(bucket_name, object_key):
    """Stream text file line by line"""
    response = s3.get_object(Bucket=bucket_name, Key=object_key)
    streaming_body = response['Body']
    
    for line in streaming_body.iter_lines():
        yield line.decode('utf-8')