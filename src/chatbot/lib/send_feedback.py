import json
from google.cloud import pubsub_v1
from config import TOPIC_ID, PROJECT_ID


def replace_dict_value_double_quote_by_single_quote(data_dict):
    for key in data_dict:
        if isinstance(data_dict[key], str):
            data_dict[key] = data_dict[key].replace('"', "'")
    return data_dict


def encode_data(data_dict):
    # We need to be careful to replace " by ' to prevent errors in the string defintion
    data_single_quote = replace_dict_value_double_quote_by_single_quote(data_dict)
    json_dict = json.dumps(data_single_quote)
    json_dict_str = str(json_dict)
    data_dict = json_dict_str.encode("utf-8")
    return data_dict


def send_to_pubsub(data_dict):
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)

    message = encode_data(data_dict)

    _ = publisher.publish(topic_path, message)
