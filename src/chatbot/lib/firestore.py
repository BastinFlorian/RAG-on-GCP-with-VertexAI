import logging
import numpy as np
import firebase_admin
import datetime as dt

from google.cloud import aiplatform
from firebase_admin import firestore
from typing import List, Dict, Any, Union
from langchain.schema import BaseRetriever, Document
from langchain.embeddings.vertexai import VertexAIEmbeddings
from google.cloud.aiplatform.matching_engine import matching_engine_index_endpoint
from langchain.callbacks.manager import CallbackManagerForRetrieverRun, AsyncCallbackManagerForRetrieverRun

from .filters import convert_filters_datetime_to_timestamp, get_namespace_from_filters
from .errors_handler import traceback_not_exist_firestore_document

from config import (
    PROJECT_ID,
    FIRESTORE_DATABASE_NAME,
    REGION,
    INDEX_ENDPOINT_ID,
    DEPLOYED_INDEX_ID,
    FIRESTORE_COLLECTION_NAME,
)


if not firebase_admin._apps:
    app = firebase_admin.initialize_app()

firestore_db = firestore.Client(
    project=PROJECT_ID,
    database=FIRESTORE_DATABASE_NAME
)


class FirestoreRetriever(BaseRetriever):
    index_endpoint_name: str
    deployed_index_id: str
    embeddings: VertexAIEmbeddings
    collection: str
    top_k: int = 5
    filter: List[matching_engine_index_endpoint.Namespace]
    numeric_filter: List[matching_engine_index_endpoint.NumericNamespace]
    dict_filters: Dict[str, Any]

    def _similarity_search(self, query_emb: np.ndarray):
        """
        Perform a similarity search.

        Args:
            query_emb: Query represented as an embedding

        Returns:
            A list of documents most similar to the query
        """
        my_index_endpoint = aiplatform.MatchingEngineIndexEndpoint(
            index_endpoint_name=self.index_endpoint_name,
            location=REGION
        )

        similar_docs = my_index_endpoint.find_neighbors(
            deployed_index_id=self.deployed_index_id,
            queries=query_emb,
            num_neighbors=self.top_k,
            filter=self.filter,
            numeric_filter=self.numeric_filter
        )

        return similar_docs

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        query_embedding = self.embeddings.embed_documents([query])
        similar_docs = self._similarity_search(query_embedding)

        logging.info(f"Filters before searching relevant documents {self.dict_filters}")

        relevant_docs = []
        for doc in similar_docs[0]:
            doc_id = doc.id
            doc_ref = firestore_db.collection(self.collection).document(doc_id)
            doc = doc_ref.get()
            traceback_not_exist_firestore_document(doc)
            if doc.exists:
                relevant_docs.append(self._firestore_doc_to_langchain_doc(doc))
        return relevant_docs

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: AsyncCallbackManagerForRetrieverRun
    ) -> List[Document]:
        raise NotImplementedError()

    def _firestore_doc_to_langchain_doc(self, fs_doc) -> Document:
        lc_doc = Document(
            page_content=fs_doc.get("content"),
            metadata={
                "source": fs_doc.get("source"),
                "title": fs_doc.get("title"),
            }
        )
        return lc_doc


def get_retriever(embeddings: VertexAIEmbeddings, filters: Dict[str, Union[bool, dt.date]]):
    filters = convert_filters_datetime_to_timestamp(filters)
    filter, numeric_filter = get_namespace_from_filters(filters)

    retriever = FirestoreRetriever(
        index_endpoint_name=INDEX_ENDPOINT_ID,
        deployed_index_id=DEPLOYED_INDEX_ID,
        collection=FIRESTORE_COLLECTION_NAME,
        embeddings=embeddings,
        top_k=5,
        filter=filter,
        numeric_filter=numeric_filter,
        dict_filters=filters
    )
    return retriever
