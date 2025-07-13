import mimetypes
import os
import boto3
from botocore.exceptions import ClientError
import re
from app.config.default import Settings
from app.utils.api import APP_ERROR, StatusCode

class Storage:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._client = boto3.client('s3')
        return cls._instance

    def get_file(self, bucket: str, key: str) -> bytes:
        """
        Downloads a file from S3 and returns its content as bytes.
        
        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The path (key) of the file in the bucket.
        
        Returns:
            bytes: The content of the file.
        
        Raises:
            ClientError: If the file does not exist or other boto3 error occurs.
        """
        try:
            response = self._client.get_object(Bucket=bucket, Key=key)
            body = response['Body'].read()
            return body
        except ClientError as e:
            print(f"Error retrieving {key} from {bucket}: {e}")
            raise
    
    def get_sorted_file_keys(self, bucket, prefix):
        paginator = self._client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

        all_keys = []
        for page in page_iterator:
            contents = page.get('Contents', [])
            for obj in contents:
                key = obj['Key']
                if key != prefix and not key.endswith('/'):
                    all_keys.append(key)

        def sort_key(key):
            filename = key.rsplit('/', 1)[-1]
            match = re.match(r'(\d+)', filename)
            return (int(match.group(1)) if match else float('inf'), filename)

        return sorted(all_keys, key=sort_key)
    
    def generate_sequential_upload_presigned_url(self, bucket: str, prefix: str, count: int, file_ext: str):
        file_keys = self.get_sorted_file_keys(bucket=bucket, prefix=prefix)
        urls = []
        
        last_count = 0
        for key in file_keys:
            file_name = os.path.basename(key)
            file_base_name = os.path.splitext(file_name)[0].lower()
            file_base_name_int = int(file_base_name)
            if file_base_name_int > last_count:
                last_count = file_base_name_int

        initial_file = last_count + 1
        for i in range(count):
            file_name = f"{initial_file + i}{file_ext}"
            s3_key = f"{prefix}/{file_name}"
            content_type_guess = mimetypes.guess_type(f"file{file_ext}")
            content_type = content_type_guess[0] or 'application/octet-stream'
            try:
                presigned_url = self._client.generate_presigned_url(
                    ClientMethod="put_object",
                    Params={
                        "Bucket": bucket,
                        "Key": s3_key,
                        "ContentType": content_type
                    },
                    ExpiresIn=Settings.S3_SIGNED_URL_EXPIRY
                )
            except Exception as e:
                raise APP_ERROR(status_code=StatusCode.SOMETHING_WENT_WRONG, code="docProcessor/storage/something-went-wrong", message="Could not generate signed URL")

            urls.append({
                "filename": f"{file_name}",
                "path": s3_key,
                "uploadURL": presigned_url
            })

        return urls

    def get_folder_size(self, bucket, prefix):
        total_size = 0
        continuation_token = None

        while True:
            if continuation_token:
                response = self._client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix,
                    ContinuationToken=continuation_token
                )
            else:
                response = self._client.list_objects_v2(
                    Bucket=bucket,
                    Prefix=prefix
                )

            for obj in response.get("Contents", []):
                total_size += obj["Size"]

            if response.get("IsTruncated"):
                continuation_token = response.get("NextContinuationToken")
            else:
                break

        return total_size

    def delete_file(self, bucket: str, key: str) -> bool:
        """
        Deletes a file from S3.
        
        Args:
            bucket (str): The name of the S3 bucket.
            key (str): The path (key) of the file in the bucket.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        
        Raises:
            APP_ERROR: If deletion fails with custom error message.
        """
        try:
            self._client.delete_object(Bucket=bucket, Key=key)
            return True
        except ClientError as e:
            print(f"Error deleting {key} from {bucket}: {e}")
            raise APP_ERROR(
                status_code=StatusCode.SOMETHING_WENT_WRONG,
                code="docProcessor/storage/delete-failed",
                message=f"Could not delete file: {str(e)}"
            )
