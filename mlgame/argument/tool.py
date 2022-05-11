import json


def get_data_from_json_file(file_path) -> dict:
    """
    open json file and return dict data
    """
    with open(file=file_path, mode="rb") as f:
        config_data = json.load(f)
    return config_data


