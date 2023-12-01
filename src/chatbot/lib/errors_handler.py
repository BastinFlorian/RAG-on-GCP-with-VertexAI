import logging
from google.cloud.firestore_v1.document import DocumentReference


def traceback_not_exist_firestore_document(doc: DocumentReference):
    if not doc.exists:
        logging.error(f"""
            The document {doc.id} does not exists in Firestore but was reqeusted by Vector Search.
            The Vector Search should be updated when new contents are added in GCS and Firestore.
            Have a look at `gcloud ai index update` command
        """)


def traceback_no_document_found_in_firestore():
    logging.error("""
        No document were found in Firestore
        Vector Search requested some documents IDs but no one is in Firestore
        The Vector Search should be updated when new contents are added in GCS and Firestore.
        Have a look at `gcloud ai index update` command

    """)


def traceback_no_urls_retrieved():
    logging.error("""
        No urls sources retrieved for your question
        It is related to the not found Firestore document
    """)
