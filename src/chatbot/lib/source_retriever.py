import collections
from typing import List
from langchain.schema import Document
from .errors_handler import traceback_no_document_found_in_firestore


def list_top_k_sources(source_documents: List[Document], k=3) -> str:
    """
    Get the top k sources from a list of documents.

    Counts the number of chunks per documents and sorts them in descending order.
    Displays a markdown format string with the top k sources.

    Args:
        source_documents : List[Document]
            A list of Document objects.
        k : int, optional
            The number of sources to display. Default is 3.

    Returns:
        str
            A markdown formatted string to be displayed in the frontend.
    """
    if not source_documents:
        traceback_no_document_found_in_firestore()
        return ""

    sources = [
        f'[{source_document.metadata["title"]}]({source_document.metadata["source"]})'
        for source_document in source_documents
    ]

    if sources:
        k = min(k, len(sources))
        distinct_sources = list(zip(*collections.Counter(sources).most_common()))[0][:k]
        distinct_sources_str = "  \n- ".join(distinct_sources)
        return f"Source(s):  \n- {distinct_sources_str}"


def get_top_k_urls(source_documents: List[Document], k=3) -> List[str]:
    """
    Retrieve the top k distinct source URLs from a list of source documents.

    Args:
        source_documents (List[Document]): A list of source documents.
        k (int, optional): The number of distinct source URLs to retrieve. Defaults to 3.

    Returns:
        List[str]: A list of the top k distinct source URLs.

    Raises:
        None

    """
    if not source_documents:
        traceback_no_document_found_in_firestore()
        return list()

    urls = [source_document.metadata["source"] for source_document in source_documents]
    k = min(k, len(urls))
    distinct_urls = list(zip(*collections.Counter(urls).most_common()))[0][:k]
    return distinct_urls
