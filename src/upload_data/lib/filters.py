
from .typehint import HintDataFrame


def get_metadata_from_active_pages(
    df: HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at']] # noqa
) -> HintDataFrame[['page_id', 'space_key', 'created_at', 'modified_at', 'metadata']]: # noqa
    """
    Create metadata column from active pages
    It allows us to apply filter in the vector search
    Fore more information on the format,
    see: https://cloud.google.com/vertex-ai/docs/vector-search/filtering?hl=fr#denylist
    """
    df['metadata'] = df.apply(lambda x: get_metadata_str_from_namespace(x['modified_at'], x['space_key']), axis=1)
    return df


def get_metadata_str_from_namespace(modified_at: int, space_key: str):
    """ To understand this specific format to GCP,
    see: https://cloud.google.com/vertex-ai/docs/vector-search/filtering?hl=fr#specify-namespaces-tokens-or-values
    """
    metadata_str = """ {"restricts": [{"namespace": "space_key", "allow": [""" + '"' + space_key + '"]}]'
    metadata_str += ","
    metadata_str += """ "numeric_restricts": [{"namespace": "modified_at", "value_int": """ + str(modified_at) + """}]}"""  # noqa
    return metadata_str
