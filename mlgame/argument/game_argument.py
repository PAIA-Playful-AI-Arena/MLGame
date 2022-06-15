import importlib
from argparse import ArgumentParser
from os import path

from pydantic import ValidationError

from mlgame.argument.tool import get_data_from_json_file
from mlgame.argument.model import UserNumConfig
from mlgame.core.exceptions import GameConfigError


def create_game_params_parser(parser_config: dict):
    """
    Generate `argparse.ArgumentParser` from `parser_config`

    @param parser_config A dictionary carries parameters for creating `ArgumentParser`.
           The key "()" specifies parameters for constructor of `ArgumentParser`,
           its value is a dictionary of which the key is the name of parameter and
           the value is the value to be passed to that parameter.
           The remaining keys of `parser_config` specifies arguments to be added to the parser,
           which `ArgumentParser.add_argument() is invoked`. The key is the name
           of the argument, and the value is similar to the "()"
           but for the `add_argument()`. Note that the name of the key is used as the name
           of the argument, but if "name_or_flags" is specified in the dictionary of it,
           it will be passed to the `add_argument()` instead. The value of "name_or_flags"
           must be a tuple.
           An example of `parser_config`:
           ```
            {
                "()": {
                    "usage": "game <difficulty> <level>"
                },
                "difficulty": {
                    "choices": ["EASY", "NORMAL"],
                    "metavar": "difficulty",
                    "help": "Specify the game style. Choices: %(choices)s"
                },
                "level": {
                    "type": int,
                    "help": "Specify the level map"
                },
            }
           ```
    """
    if parser_config.get("()"):
        parser = ArgumentParser(**parser_config["()"])
    else:
        parser = ArgumentParser()

    for arg_name in parser_config.keys():
        if arg_name != "()":
            arg_config = parser_config[arg_name].copy()

            name_or_flag = arg_config.pop("name_or_flags", None)
            if not name_or_flag:
                name_or_flag = (arg_name,)

            parser.add_argument(*name_or_flag, **arg_config)

    return parser


def parse_game_config_data(game_config_data: dict):
    """
    parse game parameter and generate data for argument parser
    """
    # TODO to optimize
    result = {}
    params = game_config_data["game_params"]
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
        if "min" in param and "max" in param:
            obj["choices"] = range(param["min"], param["max"] + 1)
        """
        ex -t --time_to_play
        """
        if "flag" in param:
            obj["name_or_flags"] = (f'-{param["flag"]}', f'--{param["name"]}')
        else:
            obj["name_or_flags"] = (f'--{param["name"]}',)

        result[param["name"]] = obj
    result["()"] = {
        "prog": game_config_data["game_name"],
        "game_usage": game_usage
    }
    return result


class GameConfig:
    """
    The data class storing the game defined config
    Included game_config.json game_cls
    """

    def __init__(self, game_folder: str):
        """
        Parse the game defined config and generate a `GameConfig` instance
        """
        game_config = self._load_game_config(game_folder)

        config_data = get_data_from_json_file(path.join(game_folder, "game_config.json"))
        try:
            self.game_version = config_data["version"]
            self.user_num_config = UserNumConfig(**config_data["user_num"])
            self._process_game_param_dict(config_data)
            self.game_config_parser = create_game_params_parser(self._config_to_create_parser)
            self.game_cls = None
            game_setup = getattr(game_config, "GAME_SETUP")
            self.game_cls = game_setup["game"]
        except AttributeError:
            raise GameConfigError("Missing variable 'GAME_SETUP' in the config.py")
        except KeyError:
            raise GameConfigError(f"game_config.json in {game_folder} "
                                  f"should contains 'user_num', 'version', 'game_params' ")
        except ValidationError:
            raise GameConfigError(f"`user_num` in game_config.json should contains 'min' and 'max' "
                                  f"and user_num['min'] < user_num['max']")
        # self._process_game_setup_dict()

    def parse_game_params(self, game_params) -> dict:
        return self.game_config_parser.parse_args(game_params).__dict__

    def _load_game_config(self, game_folder):
        """
        Load the game config
        """
        try:
            # game_config = importlib.import_module(f"{game_folder}.config")

            spec = importlib.util.spec_from_file_location("config", path.join(game_folder, "config.py").__str__())
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            game_config = module
        except ModuleNotFoundError as e:
            # print which module is not found or installed at which game_folder
            failed_module_name = e.__str__().split("'")[1]
            msg = f"Module '{failed_module_name}' is not found in game process"
            raise GameConfigError(msg)
        else:
            return game_config

    def _process_game_param_dict(self, config_data):
        """
        Convert some fields in `GAME_PARAMS`
        """
        self._config_to_create_parser = parse_game_config_data(config_data)

        # Append the prefix of MLGame.py usage to the `game_usage`
        # and set it to the `usage`
        if self._config_to_create_parser.get("()") and self._config_to_create_parser["()"].get("game_usage"):
            game_usage = str(self._config_to_create_parser["()"].pop("game_usage"))
            self._config_to_create_parser["()"]["usage"] = "python MLGame.py [options] " + game_usage

        # If the game not specify "--version" flag,
        # try to convert `GAME_VERSION` to a flag
        if not self._config_to_create_parser.get("--version"):
            self._config_to_create_parser["--version"] = {
                "action": "version",
                "version": self.game_version
            }
