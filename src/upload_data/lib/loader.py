from langchain.schema import Document
from langchain.document_loaders import ConfluenceLoader


from config import (
    CONFLUENCE_URL,
    CONFLUENCE_API_KEY,
    CONFLUENCE_USERNAME,
)


def init_loader(
    confluence_url=CONFLUENCE_URL,
    username=CONFLUENCE_USERNAME,
    api_key=CONFLUENCE_API_KEY
) -> ConfluenceLoader:
    loader = ConfluenceLoader(
        url=confluence_url,
        username=username,
        api_key=api_key
    )
    return loader


def load_page(
    page_id: str,
    loader: ConfluenceLoader,
    keep_markdown_format: bool = True,
) -> Document:
    """Load HTML files from Confluence"""
    docs = loader.load(
        page_ids=[page_id],
        keep_markdown_format=keep_markdown_format,
        limit=1,  # Important to avoid loading all the pages
        max_pages=0  # https://github.com/langchain-ai/langchain/discussions/11634
    )
    # Issue Langchain: https://github.com/langchain-ai/langchain/issues/13579
    return docs[-1]
