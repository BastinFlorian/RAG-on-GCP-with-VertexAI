from google.cloud import storage
from typing import List
from config import (
    PROJECT_ID,
    BUCKET_NAME
)


def write_list_of_str_in_gcs(bucket_name, blob_name, list_of_str: List[str], newline=False):
    """Write and read a blob from GCS using file-like IO"""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    if newline:
        add_list_str_with_newline(blob, list_of_str)
    else:
        add_list_str_without_new_line(blob, list_of_str)


def write_str_in_gcs(bucket_name, blob_name, string_to_write: List[str]):
    """Write and read a blob from GCS using file-like IO"""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    add_str_without_new_line(blob, string_to_write)


def add_list_str_with_newline(blob, list_of_str):
    """
    Example:
    content = ["a", "b", "c"]
    file = "a\nb\nc"
    """
    with blob.open("w") as f:
        f.write("\n".join(list_of_str))


def add_list_str_without_new_line(blob, list_of_str):
    """
    Example:
    content = ["a", "b", "c"]
    file = "abc"
    """
    with blob.open("w") as f:
        for row in list_of_str:
            f.write(row)


def add_str_without_new_line(blob, string_to_write):
    with blob.open("w", encoding="utf-8") as f:
        f.write(string_to_write)


def copy_blob(blob_name, destination_blob_name, bucket_name=BUCKET_NAME):
    """Copies a blob from one bucket to another with a new name."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    source_blob = bucket.blob(blob_name)
    bucket.copy_blob(source_blob, bucket, destination_blob_name)


def delete_all_gcs_files_in_directory(directory_name, bucket_name=BUCKET_NAME):
    """Deletes all the blobs in the bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=directory_name)
    for blob in blobs:
        blob.delete()


def delete_list_of_gcs_files_in_directory(files_list: List[str], directory_name, bucket_name=BUCKET_NAME):
    """Deletes all the blobs in the bucket."""
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name)
    blobs = bucket.list_blobs(prefix=directory_name)
    for blob in blobs:
        if blob.name in files_list:
            blob.delete()
