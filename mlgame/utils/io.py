import json
import os

from orjson import orjson


def save_json(dest_folder, game_result:dict):
    try:
        with open(os.path.join(dest_folder,"result.json"), "w") as f:
            f.write(orjson.dumps(game_result).decode())
        pass
    except Exception as e:
        print(f"Save result.json in {dest_folder} failed. Game result is : {game_result}")



def check_folder_existed_and_readable_or_create(path):
    if not os.path.exists(path):
        os.makedirs(path)

    if os.path.isdir(path) and os.access(path, os.R_OK):
        return path
    else:
        raise NotADirectoryError(f'{path} is not a readable directory or does not exist')
