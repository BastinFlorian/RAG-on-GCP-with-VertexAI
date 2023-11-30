import os
import logging
from google.cloud import aiplatform
from upload_data.lib.typehint import HintDataFrame
from upload_data.lib.gcs import copy_blob, delete_all_gcs_files_in_directory
from upload_data.lib.process_new_pages import process_new_pages
from upload_data.lib.firestore import delete_collection, init_firestore_db
from upload_data.lib.filters import get_metadata_from_active_pages
from upload_data.lib.get_confluence_pages import (
    get_confluence_active_pages_and_metadata,
    write_confluence_active_pages_in_gcs
)

from upload_data.config import (
    INDEX_ID,
    PROJECT_ID,
    REGION,
    BUCKET_NAME,
    GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
    GCS_ACTIVE_PAGES_LIST_FILENAME,
    GCS_PREVIOUS_PAGES_LIST_FILENAME,
    FIRESTORE_COLLECTION_NAME,
    GCS_EMBEDDING_DIRECTORY,
    GCS_EMBEDDING_TO_DELETE_DIRECTORY
)


def main(batch_size=10):
    "List all confluence and load then by batch of [batch_size] pages"
    logging.info("Start initialization of data")

    # Reset documents in Firestore
    logging.info("Reset documents in Firestore")
    firestore_db = init_firestore_db()
    delete_collection(firestore_db.collection(FIRESTORE_COLLECTION_NAME), batch_size=100)

    # Reset files in GCS
    logging.info("Reset documents in GCS")
    delete_all_gcs_files_in_directory(directory_name=GCS_EMBEDDING_DIRECTORY)
    delete_all_gcs_files_in_directory(directory_name=GCS_EMBEDDING_TO_DELETE_DIRECTORY)

    logging.info(" Load active Confluence pages in GCS")
    df_active_pages: HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at']] = get_confluence_active_pages_and_metadata()  # noqa

    # Add metadata used to filter points in the vector search
    df_active_pages: HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at', 'metadata']] = get_metadata_from_active_pages(df_active_pages)  # noqa

    logging.info("Processing new pages")
    # Generate chunks embeddings for all pages and save in GCS
    process_new_pages(df_active_pages=df_active_pages)

    # Set active pages
    logging.info("Writing new pages list in GCS")
    write_confluence_active_pages_in_gcs(df_active_pages)

    # Set active pages to previous pages
    logging.info("Copy active pages list to previous pages list in GCS")
    copy_blob(
        bucket_name=BUCKET_NAME,
        blob_name=os.path.join(GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY, GCS_ACTIVE_PAGES_LIST_FILENAME),
        destination_blob_name=os.path.join(GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY, GCS_PREVIOUS_PAGES_LIST_FILENAME)
    )

    # Update the vertex Index
    gcs_embedding_uri = 'gs://' + BUCKET_NAME + '/' + GCS_EMBEDDING_DIRECTORY
    rag_index = aiplatform.MatchingEngineIndex(
        index_name=INDEX_ID,
        project=PROJECT_ID,
        location=REGION
    )
    rag_index.update_embeddings(
        contents_delta_uri=gcs_embedding_uri,
        is_complete_overwrite=True
    )


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    main()
