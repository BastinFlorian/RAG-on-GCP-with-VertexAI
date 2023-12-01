# To have the modified Confluence pages, we need to compare the previous and the current Confluence pages.
# To compare the previous and the current Confluence pages, we need to load the previous and the current
# Confluence pages.
# To get the new pages, we need to get the current Confluence pages that are not in the previous Confluence pages.
# To get the modified pages, we need to get the current Confluence pages that are in the previous
# Confluence pages but have a different modified date.
# To get the deleted pages, we need to get the previous Confluence pages that are not in the current Confluence pages.

import os
import pandas as pd

from config import (
    BUCKET_NAME,
    GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
    GCS_ACTIVE_PAGES_LIST_FILENAME,
    GCS_PREVIOUS_PAGES_LIST_FILENAME
)


def get_df_of_pages_to_add_and_delete():
    """Useful to know if we need to update and what to update in the Vector Search Index"""
    # Load
    active_pages_path = os.path.join(
        "gs://",
        BUCKET_NAME,
        GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
        GCS_ACTIVE_PAGES_LIST_FILENAME
    )
    df_active_pages = pd.read_csv(active_pages_path)

    previous_pages_path = os.path.join(
        "gs://",
        BUCKET_NAME,
        GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
        GCS_PREVIOUS_PAGES_LIST_FILENAME
    )

    try:
        df_previous_pages = pd.read_csv(previous_pages_path)
    except FileNotFoundError:
        raise FileNotFoundError(f"""
            Previous pages file not found in {previous_pages_path}
            Are you sure you did the initialization step before the update ?
            At first step, no previous confleunce pages file is available.
        """)

    df_active_pages.page_id = df_active_pages.page_id.astype(str)
    df_previous_pages.page_id = df_previous_pages.page_id.astype(str)

    # Detect new, modified and deleted pages
    df_new = get_new_pages(df_active_pages, df_previous_pages)
    df_modified = get_modified_pages(df_active_pages, df_previous_pages)
    df_deleted = get_deleted_pages(df_active_pages, df_previous_pages)

    # A modified page is considered as a deleted and new added page
    # It will belongs to both df_new and df_deleted
    df_new = pd.concat([df_new, df_modified], ignore_index=True)
    df_deleted = pd.concat([df_deleted, df_modified], ignore_index=True)

    return df_new, df_deleted


def get_new_pages(df_new, df_previous):
    # New pages are pages that are not in previous pages because they are just added
    df_new = df_new[~df_new['page_id'].isin(df_previous['page_id'])]
    return df_new


def get_modified_pages(df_new, df_previous):
    # Modified pages are pages that are in previous pages and in new pages but have a different modified date
    df_new = df_new.merge(df_previous, on='page_id', how='left')
    df_new = df_new[df_new['modified_at_x'] > df_new['modified_at_y']]
    return df_new


def get_deleted_pages(df_new, df_previous):
    # Deleted pages are pages that are in previous pages but not in new pages
    df_previous = df_previous[~df_previous['page_id'].isin(df_new['page_id'])]
    return df_previous
