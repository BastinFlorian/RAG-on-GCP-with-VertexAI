
from google.cloud import firestore
from config import (
    FIRESTORE_COLLECTION_NAME,
    PROJECT_ID,
    FIRESTORE_DATABASE_NAME
)

METADATA_KEYS_TO_ADD = [
        'source',
        'title',
        'id'
        'Titre 1',
        'Sous-titre 1',
        'Sous-titre 2'
    ]


def create_json_from_langchain_document(langchain_document):
    json_doc = {
        "content": langchain_document.page_content
    }

    for key in langchain_document.metadata.keys():
        if key in METADATA_KEYS_TO_ADD:
            json_doc[key] = langchain_document.metadata[key]
    return json_doc


def create_json_from_langchain_documents(langchain_documents, ids):
    list_of_json_docs = []
    for i, langchain_document in enumerate(langchain_documents):
        id = ids[i]
        json_doc = create_json_from_langchain_document(langchain_document)
        list_of_json_docs.append({str(id): json_doc})
    return list_of_json_docs


def init_firestore_db():
    # Send json text and metadata to firestore
    firestore_db = firestore.Client(
        project=PROJECT_ID,
        database=FIRESTORE_DATABASE_NAME
    )
    return firestore_db


def send_json_to_firestore(list_of_json_docs, firestore_db, firestore_collection_name=FIRESTORE_COLLECTION_NAME):
    for json_doc in list_of_json_docs:
        json_key = list(json_doc.keys())[0]
        json_value = json_doc[json_key]
        firestore_db.collection(firestore_collection_name).document(json_key).set(json_value)


def delete_to_firestore(list_of_ids, firestore_db, firestore_collection_name=FIRESTORE_COLLECTION_NAME):
    for json_key in list_of_ids:
        firestore_db.collection(firestore_collection_name).document(json_key).delete()


def delete_collection(coll_ref, batch_size):
    docs = coll_ref.list_documents(page_size=batch_size)
    deleted = 0

    for doc in docs:
        doc.delete()
        deleted = deleted + 1

    if deleted >= batch_size:
        return delete_collection(coll_ref, batch_size)
