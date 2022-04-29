import os
import sys
from argparse import ArgumentParser, REMAINDER

import pydantic

from mlgame.argument.model import MLGameArgument, GameConfig
from mlgame.core.exceptions import GameConfigError
from mlgame.gamedev.paia_game import get_paia_game_obj, PaiaGame
from mlgame.utils.logger import logger
from mlgame.version import version


def create_cli_args_parser():
    """
    Generate an ArgumentParser for parse the arguments in the command line
    """
    usage_str = ("python %(prog)s [options] <game_folder> [game_params]")
    description_str = ("A platform for applying machine learning algorithm "
                       "to play pixel games. "
                       "In default, the game runs in the machine learning mode. ")

    parser = ArgumentParser(usage=usage_str, description=description_str,
                            add_help=False)

    parser.add_argument("game_folder",
                        type=os.path.abspath,
                        nargs="?",
                        help="the name of the game to be started")
    parser.add_argument("game_params", nargs=REMAINDER, default=None,
                        help="[optional] the additional settings for the game. "
                             "Note that all arguments after <game> will be collected to 'game_params'.")

    group = parser.add_argument_group(title="functional options")
    group.add_argument("--version", action="version", version=version)
    group.add_argument("-h", "--help", action="store_true",
                       help="show this help message and exit. "
                            "If this flag is specified after the <game>, "
                            "show the help message of the game instead.")

    group.add_argument("-f", "--fps", type=int, default=30,
                       help="the updating frequency of the game process [default: %(default)s]")

    group.add_argument("-1", "--one-shot", action="store_true",
                       dest="one_shot_mode",
                       help="quit the game when the game is passed or is over. "
                            "Otherwise, the game will restart automatically. [default: %(default)s]")
    group.add_argument("-nd", "--no-display", action="store_true",
                       dest="no_display",
                       help="didn't display the game on screen. [default: %(default)s]")
    group.add_argument("--ws_url",
                       type=str,
                       dest="ws_url",
                       help="ws_url route")

    group.add_argument("-i", "--input-ai",
                       # type=validate_file,
                       type=os.path.abspath,
                       action="append",
                       dest="ai_clients",
                       default=None, metavar="SCRIPT",
                       help="specify user script(s) for the machine learning mode. "
                            "For multiple user scripts, use this flag multiple times. "
                            "The script path could be relative path or absolute path "
                       )

    return parser


def parse_cmd_and_get_arg_obj(arg_str: str) -> MLGameArgument:
    arg_parser = create_cli_args_parser()
    try:
        parsed_args = arg_parser.parse_args(arg_str.split())
    except pydantic.ValidationError as e:
        logger.exception(f"Error in parsing command : {e.__str__()}")
        arg_parser.print_help()
        sys.exit()

    if parsed_args.help:
        arg_parser.print_help()
        sys.exit()
    else:
        # TODO version
        pass
    arg_obj = MLGameArgument(**parsed_args.__dict__)
    return arg_obj


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
