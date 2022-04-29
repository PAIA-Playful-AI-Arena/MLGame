import sys
from argparse import ArgumentParser

import pydantic

from mlgame.argument.model import GameConfig, MLGameArgument
from mlgame.core.exceptions import GameConfigError
from mlgame.gamedev.paia_game import get_paia_game_obj, PaiaGame
from mlgame.utils.logger import logger


def create_game_arg_parser(parser_config: dict):
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


def create_paia_game_obj(arg_obj: MLGameArgument) -> PaiaGame:
    try:
        # 2. parse game_folder/config.py and get game_config
        game_config = GameConfig(arg_obj.game_folder.__str__())
    except pydantic.ValidationError as e:
        logger.error(f"Error in parsing command : {e.__str__()}")

        sys.exit()
    except GameConfigError as e:
        logger.exception(f"Error in parsing game parameter : {e.__str__()}")
        # logger.info("game is exited")
        sys.exit()
    # 3. get parsed_game_params
    # Program will catch parse error (error in game parameter in cli) here.
    param_parser = create_game_arg_parser(game_config.game_params)
    parsed_game_params = param_parser.parse_args(arg_obj.game_params)
    # if parse config error game will exit at system code 2
    game_setup = game_config.game_setup
    game_cls = game_setup["game"]
    return get_paia_game_obj(game_cls, parsed_game_params.__dict__)
