import os

from minio_client import MINIO_BUCKET, minio_client


def get_image_path(filename: str) -> str:
    return f"tmp/{filename}"


def delete_image(filename: str):
    filepath = get_image_path(filename)

    if os.path.exists(filepath):
        os.remove(filepath)


def download_image(filename: str):
    filepath = get_image_path(filename)
    directory = os.path.dirname(filepath)

    if not os.path.exists(directory):
        os.makedirs(directory)

    response = minio_client.get_object(MINIO_BUCKET, filename)

    with open(filepath, "wb") as f:
        f.write(response.read())


def download_db_images(db_path: str):
    objects = minio_client.list_objects(MINIO_BUCKET, recursive=True)

    for obj in objects:
        if obj.object_name.startswith(db_path):
            filepath = get_image_path(obj.object_name)
            directory = os.path.dirname(filepath)

            if not os.path.exists(directory):
                os.makedirs(directory)

            response = minio_client.get_object(MINIO_BUCKET, obj.object_name)

            with open(filepath, "wb") as f:
                f.write(response.read())


def delete_db_images(db_path: str):
    objects = minio_client.list_objects(MINIO_BUCKET, recursive=True)

    for obj in objects:
        if obj.object_name.startswith(db_path):
            filepath = get_image_path(obj.object_name)

            if os.path.exists(filepath):
                os.remove(filepath)
