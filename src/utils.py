import json
import logging

from yaml import FullLoader, load


def load_config(file_path):
    with open(file_path, 'r') as fp:
        file_config = fp.read()
    config = load(file_config, FullLoader)

    return config


def oauth_decode(data):
    new_data = data.decode("utf-8", "strict")

    return json.loads(new_data)
