
import json
import uuid
import time
import logging
import numpy as np
import functools
from typing import Generator, List, Tuple, Optional, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from vertexai.language_models import TextEmbeddingModel


def encode_texts_to_embeddings(
    embedding_model: TextEmbeddingModel,
    chunks: List[str]
) -> List[Optional[List[float]]]:
    "Define an embedding method that uses the model"
    try:
        embeddings = embedding_model.get_embeddings(chunks)
        return [embedding.values for embedding in embeddings]
    except Exception as err:
        logging.error(f"""
                      Error while encoding text to embedding: {err}, sentence: {chunks}
                      The whole batch will be ignored.
                    """)
        return [None for _ in range(len(chunks))]


def generate_batches(chunks: List[str], batch_size: int) -> Generator[List[str], None, None]:
    "Generator function to yield batches of chunks"
    for i in range(0, len(chunks), batch_size):
        yield chunks[i: i + batch_size]


def encode_text_to_embedding_batched(
    embedding_model: TextEmbeddingModel,
    chunks: List[str],
    api_calls_per_second: int = 10,
    batch_size: int = 5
) -> Tuple[List[bool], np.ndarray]:
    """
    Encodes a batch of chunks into embeddings using a text embedding model.
    Be careful to Vertex Embedding quotas: https://cloud.google.com/vertex-ai/docs/quotas?hl=fr#generative-ai

    Parameters
    ----------
    embedding_model : TextEmbeddingModel
        The text embedding model to use for encoding.
    chunks : List[str]
        The list of chunks to encode.
    api_calls_per_second : int, optional
        The number of API calls per second to limit the rate of encoding, by default 10.
    batch_size : int, optional
        The batch size for encoding, by default 5.

    Returns
    -------
    Tuple[List[bool], np.ndarray]
        A tuple containing a list of booleans indicating the success of encoding for each sentence,
        and a numpy array of the successful embeddings.
    """
    embeddings_list: List[List[float]] = []

    # Prepare the batches using a generator
    batches = generate_batches(chunks, batch_size)

    seconds_per_job = 1 / api_calls_per_second

    with ThreadPoolExecutor() as executor:
        futures = []
        for batch in batches:
            futures.append(
                executor.submit(functools.partial(encode_texts_to_embeddings), embedding_model, batch)
            )
            time.sleep(seconds_per_job)

        for future in futures:
            embeddings_list.extend(future.result())

    is_successful = [
        embedding is not None for _, embedding in zip(chunks, embeddings_list)
    ]
    embeddings_list_successful = np.squeeze(
        np.stack([embedding for embedding in embeddings_list if embedding is not None])
    )

    if embeddings_list_successful.ndim == 1:
        # Add one dimension to fit for batch embeddings
        embeddings_list_successful = [embeddings_list_successful]
    return is_successful, embeddings_list_successful


def get_json_formatted(
    is_successful: List[bool],
    embedding_list: List[np.ndarray],
    matadata_dict: Dict[str, Any],
    ids: List[uuid.UUID]
) -> List[str]:
    """
    Format the embeddings as JSON strings.

    Parameters:
        is_successful (List[bool]): A list of boolean values indicating whether the embedding was successful for each
        item.
        embedding_list (List[np.ndarray]): A list of Numpy arrays representing the embeddings.
        matadata_dict (Dict[str, Any]): A dictionary containing metadata information useful for Vector filtering.
        ids (List[uuid.UUID]): A list of UUIDs representing the IDs of the items.

    Returns:
        List[str]: A list of JSON-formatted strings representing the embeddings.


    Example:
        is_successful = [True, False, True]
        embedding_list = [np.array([1, 2, 3]), None, np.array([4, 5, 6])]
        matadata_dict = {"key": "value"}
        ids = [uuid.uuid4(), uuid.uuid4(), uuid.uuid4()]

        >>> print(get_json_formatted(is_successful, embedding_list, matadata_dict, ids))

        [
            '{"id": "chdye56d-6678-4f1c-9a8c-ezrfeiub3345", "embedding": ["1", "2", "3"], "key": "value"} \n',
            '{"id": "c5c9f0b4-1234-4f1c-9a8c-3a6c0d0e6e7e", "embedding": ["4", "5", "6"], "key": "value"} \n'
        ]

    """
    ids = [id for id, successfully_embeded in zip(ids, is_successful) if successfully_embeded]
    embeddings_formatted = []
    for (id, embedding) in zip(ids, embedding_list):
        data_dict = {
            "id": str(id),
            "embedding": [str(value) for value in embedding],
        }
        data_dict.update(matadata_dict)
        embeddings_formatted.append(json.dumps(data_dict) + "\n")

    return embeddings_formatted
