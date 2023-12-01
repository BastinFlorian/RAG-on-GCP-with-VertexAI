import os
import logging
import pandas as pd
from google.cloud import aiplatform
from lib.typehint import HintDataFrame
from lib.process_new_pages import process_new_pages
from lib.get_chunks_ids import get_id_to_delete_from_df
from lib.firestore import init_firestore_db, delete_to_firestore
from lib.get_updates_pages import get_df_of_pages_to_add_and_delete
from lib.gcs import write_str_in_gcs, copy_blob, delete_list_of_gcs_files_in_directory
from lib.get_confluence_pages import (
    get_confluence_active_pages_and_metadata,
    write_confluence_active_pages_in_gcs
)

from config import (
    INDEX_ID,
    PROJECT_ID,
    REGION,
    BUCKET_NAME,
    GCS_EMBEDDING_TO_DELETE_FILEPATH,
    GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
    GCS_PREVIOUS_PAGES_LIST_FILENAME,
    GCS_ACTIVE_PAGES_LIST_FILENAME,
    GCS_EMBEDDING_DIRECTORY
)


def main(data=None, context=None):
    firestore_db = init_firestore_db()

    # Update all active page on Confluence GCS file
    df_active_pages: HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at']] = get_confluence_active_pages_and_metadata()  # noqa
    write_confluence_active_pages_in_gcs(df_active_pages)

    # Find new and deleted pages
    # A modification is a deletion + an insertion
    df_new, df_deleted = get_df_of_pages_to_add_and_delete()

    number_of_modified_pages = pd.merge(df_new, df_deleted, how='inner', on=['page_id']).shape[0]
    logging.info(f"New pages: {df_new.shape[0] - number_of_modified_pages}")
    logging.info(f"Modified pages: {number_of_modified_pages}")
    logging.info(f"Deleted pages: {df_deleted.shape[0] - number_of_modified_pages}")

    # Get embeddings ids to delete for modified and deleted pages
    ids_to_delete = get_id_to_delete_from_df(df_deleted)

    # Write delete ids in GCS delete directory
    logging.info(f"{len(ids_to_delete)} chunks to delete")

    str_ids_to_delete = "\n".join(ids_to_delete)
    write_str_in_gcs(
        bucket_name=BUCKET_NAME,
        blob_name=GCS_EMBEDDING_TO_DELETE_FILEPATH,
        string_to_write=str_ids_to_delete,
    )
    logging.info(f"Ids to delete wrote in delete directory: {GCS_EMBEDDING_TO_DELETE_FILEPATH}")

    # Delete pages_ids.json in GCS
    delete_file_list = [f"{id_to_delete}.json" for id_to_delete in ids_to_delete]
    delete_list_of_gcs_files_in_directory(directory_name=GCS_EMBEDDING_DIRECTORY, files_list=delete_file_list)

    # Delete from Firestore if exists
    delete_to_firestore(list_of_ids=ids_to_delete, firestore_db=firestore_db)

    # Process new and modified pages and write in GCS
    logging.info("Process new and modified pages and write in GCS")
    process_new_pages(df_active_pages=df_new)

    # Copy active pages to previous pages
    logging.info("Copy active pages list to previous pages list in GCS")
    copy_blob(
        bucket_name=BUCKET_NAME,
        blob_name=os.path.join(GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY, GCS_ACTIVE_PAGES_LIST_FILENAME),
        destination_blob_name=os.path.join(GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY, GCS_PREVIOUS_PAGES_LIST_FILENAME)
    )

    if len(df_new) + len(df_deleted):
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
