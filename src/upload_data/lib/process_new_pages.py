import os
import ast
import uuid
from tqdm import tqdm
from typing import List, Tuple
from google.cloud import firestore
from google.cloud import aiplatform
from langchain.schema import Document
from langchain.document_loaders import ConfluenceLoader
from vertexai.language_models import TextEmbeddingModel

from .gcs import write_list_of_str_in_gcs
from .transformer import split_docs
from .typehint import HintDataFrame
from .loader import load_page, init_loader
from .embedding import encode_text_to_embedding_batched, get_json_formatted
from .firestore import init_firestore_db, send_json_to_firestore, create_json_from_langchain_documents

from config import (
    PROJECT_ID,
    REGION,
    BUCKET_NAME,
    GCS_EMBEDDING_DIRECTORY
)


def remove_empty_chunks(chunks: List[str], ids: List[str]) -> Tuple[List[str], List[str]]:
    """Remove empty chunks and their ids"""
    non_empty_chunks = []
    non_empty_ids = []
    for idx in range(len(chunks)):
        if chunks[idx] != "":
            non_empty_chunks.append(chunks[idx])
            non_empty_ids.append(ids[idx])
    return non_empty_chunks, non_empty_ids


def process_new_page(
    page_id: str,
    metadata: str,
    confluence_loader: ConfluenceLoader,
    firestore_db: firestore.Client,
    embedding_model: TextEmbeddingModel
):
    """
    Process a new page by loading its content, splitting it into chunks,
    encoding the chunks into embeddings, and writing the embeddings in JSON format to Google Cloud Storage.
    Send the succesfully embedded chunks to Firestore.
    More informations on the data format:
    https://cloud.google.com/vertex-ai/docs/vector-search/setup/format-structure?hl=fr#prerequisite

    Parameters:
        page_id (str): The ID of the page to be processed.
        confluence_loader: The loader object for loading the page content.
        embedding_model: The model used for encoding text into embeddings.
        metadata: str of a dict with the metadata of the page

    Returns:
        None

    Example:
        metadata = {"restricts": [{"namespace": "space_key", "allow": ["test"]}]}
        json file for two chunks:
            {"id": "1", "embedding": [1,1,1], "restricts": [{"namespace": "space_key", "allow": ["test"]}]}
            {"id": "2", "embedding": [2,2,2], "restricts": [{"namespace": "space_key", "allow": ["test"]}]}
        filename: 123456789.json (page_id.json)
    """
    doc = load_page(page_id=page_id, loader=confluence_loader)
    splitted_docs: List[Document] = split_docs([doc])

    # Create chunks, embeddings and write to GCS
    chunks: List[str] = [splitted_doc.page_content for splitted_doc in splitted_docs]
    ids = [str(uuid.uuid4()) for _ in range(len(chunks))]
    chunks, ids = remove_empty_chunks(chunks, ids)

    if not are_all_chunks_empty(chunks):
        # Get embeddings and informations about the success of the embedding
        is_successful, embedding_list = encode_text_to_embedding_batched(
            embedding_model=embedding_model,
            chunks=chunks
        )
        matadata_dict = ast.literal_eval(metadata)

        json_formatted = get_json_formatted(
            is_successful=is_successful,
            embedding_list=embedding_list,
            ids=ids,
            matadata_dict=matadata_dict
        )

        write_list_of_str_in_gcs(
            bucket_name=BUCKET_NAME,
            blob_name=os.path.join(GCS_EMBEDDING_DIRECTORY, page_id + ".json"),
            list_of_str=json_formatted,
            newline=False
        )

        # Write successfully embeded chunks to Firestore
        successful_splited_docs = [splitted_docs[i] for i in range(len(splitted_docs)) if is_successful[i]]
        successful_ids = [ids[i] for i in range(len(ids)) if is_successful[i]]
        list_of_json_docs = create_json_from_langchain_documents(
            langchain_documents=successful_splited_docs,
            ids=successful_ids,
        )

        send_json_to_firestore(
            list_of_json_docs=list_of_json_docs,
            firestore_db=firestore_db
        )


def are_all_chunks_empty(chunks: List[str]) -> bool:
    """Check if all chunks are empty"""
    return all([chunk == "" for chunk in chunks])


def process_new_pages(df_active_pages: HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at', 'metadata']]):  # noqa
    aiplatform.init(
        project=PROJECT_ID,
        location=REGION,
    )

    confluence_loader = init_loader()
    embedding_model = TextEmbeddingModel.from_pretrained("textembedding-gecko@001")
    firestore_db = init_firestore_db()

    for _, row in tqdm(df_active_pages.iterrows(), total=df_active_pages.shape[0]):
        page_id = row['page_id']
        metadata = row['metadata']
        process_new_page(
            page_id=page_id,
            metadata=metadata,
            confluence_loader=confluence_loader,
            firestore_db=firestore_db,
            embedding_model=embedding_model
        )
