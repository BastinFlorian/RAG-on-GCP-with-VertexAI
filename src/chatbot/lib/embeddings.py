
from langchain.embeddings.vertexai import VertexAIEmbeddings
from config import PROJECT_ID, REGION


def get_embedding_model():
    embeddings = VertexAIEmbeddings(project=PROJECT_ID, location=REGION)
    return embeddings
