from langchain.document_loaders import ConfluenceLoader

from src.upload_data.config import (
    CONFLUENCE_URL,
    CONFLUENCE_API_KEY,
    CONFLUENCE_SPACE_NAMES,
    CONFLUENCE_USERNAME
)


def test_confluence_config(
    confluence_url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    api_key=CONFLUENCE_API_KEY,
    space_key=CONFLUENCE_SPACE_NAMES,
):
    """Load HTML files from Confluence"""
    loader = ConfluenceLoader(
        url=confluence_url,
        username=username,
        api_key=api_key
    )

    docs = loader.load(
        space_key=space_key[0],
        limit=10
    )

    assert len(docs) > 0
