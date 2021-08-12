import json


def read_json_file(config_file):
    with open(file=config_file, mode="rb") as f:
        config_data = json.load(f)
    return config_data


def parse_config(config_data):
    result = {}
    params = config_data["game_params"]
    game_usage = "%(prog)s "
    for param in params:
        obj = {
            "metavar": param["verbose"],
            "help": param["help"]

        }
        if param["type"] == "int":
            obj["type"] = int
        elif param["type"] == "str":
            obj["type"] = str

        if "default" in param:
            obj["nargs"] = "?"
            obj["default"] = param["default"]
            game_usage += "[" + param["name"] + "] "
        else:
            game_usage += "<" + param["name"] + "> "

        if "choices" in param:
            choices = []
            for choice in param["choices"]:
                if type(choice) == dict:
                    choices.append(choice["value"])
                else:
                    choices.append(choice)
            obj["choices"] = choices
        result[param["name"]] = obj
    result["()"] = {
        "prog": config_data["game_name"],
        "game_usage": game_usage
    }
    return result
