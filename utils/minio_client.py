import os

from dotenv import load_dotenv
from minio import Minio

load_dotenv()

minio_client = Minio(
    endpoint=os.getenv("MINIO_ENDPOINT"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=os.getenv("MINIO_SECURE", "false").lower() == "true",
)


def download_file(bucket_name: str, object_name: str, local_path: str):
    if not os.path.exists(os.path.dirname(local_path)):
        os.makedirs(os.path.dirname(local_path), exist_ok=True)

    minio_client.fget_object(bucket_name, object_name, local_path)
    return local_path


def list_files(bucket_name: str, prefix: str):
    return minio_client.list_objects(bucket_name, prefix=prefix)
