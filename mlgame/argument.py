import os
import sys
from typing import List, Optional
import pydantic as pydantic
from pydantic import FilePath, validator, DirectoryPath, Required
from argparse import ArgumentParser, REMAINDER

version = "9.3.5"


def get_args_parser():
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


class MLGameArgument(pydantic.BaseModel):
    fps: int = 30
    one_shot_mode: bool = False
    ai_clients: Optional[List[FilePath]] = None
    is_manual: bool = False

    game_folder: DirectoryPath
    game_params: List[str]

    # def __init__(self,**kwargs):
    #     self.
    #     self.is_manual = self.ai_clients is None
    @validator('is_manual', always=True)
    def update_manual(cls, v, values) -> bool:
        if 'ai_clients' in values:
            return values['ai_clients'] is None
        return True


def create_MLGameArgument_obj(arg_str) -> MLGameArgument:
    arg_parser = get_args_parser()
    parsed_args = arg_parser.parse_args(arg_str.split())
    if parsed_args.help:
        arg_parser.print_help()
        sys.exit()
    arg_obj = MLGameArgument(**parsed_args.__dict__)
    return arg_obj


def get_parser_from_dict(parser_config: dict):
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
