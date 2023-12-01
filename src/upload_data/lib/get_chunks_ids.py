import os
import ast
import logging
from typing import List
from google.cloud import storage
from config import (
    PROJECT_ID,
    BUCKET_NAME,
    GCS_EMBEDDING_DIRECTORY
)


def get_id_to_delete_from_df(df):
    """From page ids that are gcs filename, get if of each chunk to delete in the Vertex Search Index GCS"""
    files_ids = []
    pages_id_to_delete = df['page_id'].tolist()
    for page_id in pages_id_to_delete:
        # Get id of file to delete
        blob_name = os.path.join(GCS_EMBEDDING_DIRECTORY, str(page_id) + ".json")
        try:
            files_ids.extend(read_id_key_from_gcs_file(blob_name))
        except FileNotFoundError:
            logging.error(f"""
                        File needed for deletion {blob_name} not found.
                        The only valid reason for its non presence is that the confluence page is empty
                        """)

    return files_ids


def read_id_key_from_gcs_file(blob_name) -> List[str]:
    """Read a file where each line is a json dict

    Example:
    file =
        {"id": 0, "embedding": [0.1, 0.2, 0.3]}
        {"id": 1, "embedding": [0.1, 0.2, 0.3]}


    ouput = ["0", "1"]
    """
    storage_client = storage.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(bucket_name=BUCKET_NAME)
    blob = bucket.blob(blob_name)
    file_ids = []
    with blob.open("r") as f:
        for row in f:
            id_embedding = ast.literal_eval(row)
            file_ids.append(id_embedding['id'])

    return file_ids
