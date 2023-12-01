"""Modules import"""
import json
import logging
import requests
import pandas as pd
from typing import Dict
from datetime import datetime
from requests.auth import HTTPBasicAuth
from config import (
    CONFLUENCE_URL,
    CONFLUENCE_API_KEY,
    CONFLUENCE_USERNAME,
    CONFLUENCE_SPACE_NAMES,
    BUCKET_NAME,
    GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY,
    GCS_ACTIVE_PAGES_LIST_FILENAME
)


def get_space_ids_from_space_names(
    confluence_url: str,
    username: str,
    api_key: str,
    space_names: list
) -> Dict[str, str]:
    """Get space id from space name and create dictionnary space_id -> space_name"""
    url = confluence_url + "/api/v2/spaces"
    auth = HTTPBasicAuth(username, api_key)
    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    all_space_names = json.loads(response.text)

    space_id_keys = dict()
    for item in all_space_names["results"]:
        if item["key"] in space_names and item["id"] not in space_id_keys.keys():
            space_id_keys[item["id"]] = item["key"]

    return space_id_keys


def get_pages_in_space_on_confluence(confluence_url, username, api_key, space_id):
    """Get all active pages on confluence"""

    url = confluence_url + "/api/v2/spaces/" + space_id + "/pages"
    auth = HTTPBasicAuth(username, api_key)
    headers = {
        "Accept": "application/json"
    }

    response = requests.request(
        "GET",
        url,
        headers=headers,
        auth=auth
    )

    response_text = json.loads(response.text)
    return response_text["results"]


def convert_tz_timestamp(x):
    """Remove TZ on datetime and convert to timestamp"""

    return int(datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ').timestamp())


def get_pages_metadata_in_space(pages_from_api_confluence, space_key):
    """Process confluence results and collect only
    url, created_date and modified_date"""

    confluence_pages_metadata = list()

    for page_metadata in pages_from_api_confluence:
        page_id = page_metadata["id"]
        created_at = page_metadata["createdAt"]
        if int(page_metadata["version"]["number"]) == 1:
            modified_at = page_metadata["createdAt"]
        elif int(page_metadata["version"]["number"]) > 1:
            modified_at = page_metadata["version"]["createdAt"]

        confluence_pages_metadata.append(
            {
                "page_id": page_id,
                "space_key": space_key,
                "created_at": convert_tz_timestamp(created_at),
                "modified_at": convert_tz_timestamp(modified_at)
            }
        )

    return confluence_pages_metadata


def get_confluence_active_pages_and_metadata(
    confluence_url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    api_key=CONFLUENCE_API_KEY,
    space_names=CONFLUENCE_SPACE_NAMES
) -> pd.DataFrame:
    """Get spaces, pages and process data"""
    space_id_keys = get_space_ids_from_space_names(
        confluence_url=confluence_url,
        username=username,
        api_key=api_key,
        space_names=space_names
    )

    space_ids = list(space_id_keys.keys())

    pages_metadata_in_spaces = list()

    for space_id in space_ids:
        active_pages = get_pages_in_space_on_confluence(
            confluence_url=confluence_url,
            username=username,
            api_key=api_key,
            space_id=space_id
        )

        pages_metadata = get_pages_metadata_in_space(
            pages_from_api_confluence=active_pages,
            space_key=space_id_keys[space_id]
        )

        pages_metadata_in_spaces += pages_metadata

    return pd.DataFrame(pages_metadata_in_spaces)


def write_confluence_active_pages_in_gcs(df_pages_metadata: pd.DataFrame):
    gcs_path = f"gs://{BUCKET_NAME}/{GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY}/{GCS_ACTIVE_PAGES_LIST_FILENAME}"
    df_pages_metadata.to_csv(gcs_path, index=False)


def main():
    df_pages_metadata = get_confluence_active_pages_and_metadata()
    logging.info("Get active pages on confluence and process metadata completed successfully")
    write_confluence_active_pages_in_gcs(df_pages_metadata)
    logging.info(f"{GCS_ACTIVE_PAGES_LIST_FILENAME} uploaded to {BUCKET_NAME}/{GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY}")


if __name__ == "__main__":
    main()
