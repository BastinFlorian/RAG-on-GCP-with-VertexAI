# Imports
# Env var
import os
from ast import literal_eval
from dotenv import load_dotenv, find_dotenv

# Env variables
_ = load_dotenv(find_dotenv())

# GCP
PROJECT_ID = os.environ['PROJECT_ID']
REGION = os.environ['REGION']

# Pub Sub
TOPIC_ID = "gen-ai-pubsub-topic"

# Firestore
FIRESTORE_DATABASE_NAME = os.environ['FIRESTORE_DATABASE_NAME']
FIRESTORE_COLLECTION_NAME = "basf-rag"

# Vertex Search
INDEX_ENDPOINT_ID = os.environ["INDEX_ENDPOINT_ID"]
DEPLOYED_INDEX_ID = os.environ["DEPLOYED_INDEX_ID"]

# https://support.atlassian.com/atlassian-account/docs/manage-api-tokens-for-your-atlassian-account/
CONFLUENCE_SPACE_NAMES = literal_eval(os.environ['CONFLUENCE_SPACE_NAMES'])

# LLM Streaming default
STREAMING_MODE = False
