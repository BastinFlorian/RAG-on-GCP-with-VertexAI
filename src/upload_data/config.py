# Imports
# Env var
import os
from ast import literal_eval
from dotenv import load_dotenv, find_dotenv

# Env variables
_ = load_dotenv(find_dotenv())

# GCP AUTH
PROJECT_ID = os.environ['PROJECT_ID']
REGION = os.environ['REGION']

# GCS
BUCKET_NAME = os.environ['BUCKET_NAME']
GCS_EMBEDDING_DIRECTORY = 'contents'
GCS_EMBEDDING_TO_DELETE_DIRECTORY = 'contents/delete/'
GCS_EMBEDDING_TO_DELETE_FILEPATH = 'contents/delete/delete_file.txt'
GCS_ACTIVE_CONFLUENCE_PAGES_DIRECTORY = 'active-pages-on-confluence'
GCS_PREVIOUS_PAGES_LIST_FILENAME = 'previous_pages.csv'
GCS_ACTIVE_PAGES_LIST_FILENAME = 'active_pages.csv'

# Firestore
FIRESTORE_DATABASE_NAME = os.environ['FIRESTORE_DATABASE_NAME']
FIRESTORE_COLLECTION_NAME = "basf-rag"

# Vertex Search
INDEX_ID = os.environ["INDEX_ID"]

# Confluence Secrets
CONFLUENCE_URL = os.environ['CONFLUENCE_URL']
CONFLUENCE_API_KEY = os.environ['CONFLUENCE_PRIVATE_API_KEY']
# https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
CONFLUENCE_SPACE_NAMES = literal_eval(os.environ['CONFLUENCE_SPACE_NAMES'])
# Hint: space_key and page_id can both be found in the URL of a page in Confluence
# https://yoursite.atlassian.com/wiki/spaces/<space_key>/pages/<page_id>
CONFLUENCE_USERNAME = os.environ['CONFLUENCE_EMAIL_ADRESS']
