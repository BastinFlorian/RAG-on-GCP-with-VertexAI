
import logging
import datetime as dt
from typing import Dict, Union
from google.cloud.aiplatform.matching_engine import matching_engine_index_endpoint


def convert_filters_datetime_to_timestamp(filters: Dict[str, Union[bool, dt.date]]):
    for key, value in filters.items():
        if isinstance(value, dt.date):
            filters[key] = int(dt.datetime.combine(value, dt.datetime.min.time()).timestamp())
            logging.info(f"Converted {key} to timestamp: {filters[key]}")
    return filters


def get_namespace_from_filters(filters: Dict[str, Union[bool, dt.date]]):
    """ Convert filters to Vector Search Namespace conditions
    For more information see source code:
    https://github.com/googleapis/python-aiplatform/blob/v1.36.4/google/cloud/aiplatform/matching_engine/matching_engine_index_endpoint.py
    or
    https://cloud.google.com/vertex-ai/docs/vector-search/filtering?
    """
    filter = [
        matching_engine_index_endpoint.Namespace(
            "space_key",
            [space_name for space_name, value in filters.items() if value is True],
            [space_name for space_name, value in filters.items() if value is False],
        ),
    ]
    logging.info(f"Filter values: {filter}")

    numeric_filter = [
        matching_engine_index_endpoint.NumericNamespace(
            "modified_at",
            value_int=filters["docs_start_date"],
            op="GREATER_EQUAL"
        ),
        # matching_engine_index_endpoint.NumericNamespace(
        #     "modified_at",
        #     value_int=filters["docs_end_date"],
        #     op="LESS_EQUAL"
        # )
    ]
    logging.info(f"Numeric filter values: {numeric_filter}")
    return filter, numeric_filter
