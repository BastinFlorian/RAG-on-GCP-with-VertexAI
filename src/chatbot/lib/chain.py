import logging
import datetime as dt
from typing import Dict, Union
from langchain.chains import RetrievalQA
from langchain.callbacks.base import BaseCallbackHandler

from .llms import get_llm
from .prompt import get_prompt
from .firestore import get_retriever
from .embeddings import get_embedding_model


def get_chain(
    filters: Dict[str, Union[bool, dt.date]],
    streaming: bool = False,
    streaming_handler: BaseCallbackHandler = None
):
    if streaming and not streaming_handler:
        raise ValueError("streaming_handler must be provided when streaming is True")

    logging.info(f"New agent created at {dt.datetime.now()}")
    embeddings = get_embedding_model()
    retriever = get_retriever(embeddings=embeddings, filters=filters)
    llm = get_llm(
        streaming=streaming,
        callbacks=streaming_handler
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=retriever,
        chain_type_kwargs={"prompt": get_prompt()},
        return_source_documents=True,
    )

    return qa
