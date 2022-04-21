import argparse
import importlib
import inspect
import os
import random
import sys
from argparse import ArgumentParser, REMAINDER

from tests.mock_included_file import MockMLPlay

version = "9.3.5"


def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f


def get_args_parser():
    """
    Generate an ArgumentParser for parse the arguments in the command line
    """
    usage_str = ("python %(prog)s [options] <game> [game_params]")
    description_str = ("A platform for applying machine learning algorithm "
                       "to play pixel games. "
                       "In default, the game runs in the machine learning mode. ")

    parser = ArgumentParser(usage=usage_str, description=description_str,
                            add_help=False)

    parser.add_argument("game", type=str, nargs="?",
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


def test_to_get_fps_and_one_shot_mode():
    fps = random.randint(10, 100)
    arg_str = f"-f {fps} " \
              " mygame --user 1 --map 2"
    arg_parser = get_args_parser()
    parsed_args = arg_parser.parse_args(arg_str.split())
    assert parsed_args.fps == fps
    assert not parsed_args.one_shot_mode

    arg_str = f"-1 " \
              " mygame --user 1 --map 2"
    arg_parser = get_args_parser()
    parsed_args = arg_parser.parse_args(arg_str.split())
    assert parsed_args.fps == 30
    assert parsed_args.one_shot_mode
    assert parsed_args.ai_clients is None
    # parse args to get file and import module class


def test_to_get_ai_module():
    arg_str = "-i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " mygame --user 1 --map 2"
    arg_parser = get_args_parser()
    parsed_args = arg_parser.parse_args(arg_str.split())
    assert parsed_args.ai_clients
    # parse args to get file and import module class
    for file in parsed_args.ai_clients:
        module_name = os.path.basename(file)
        module_name = module_name.replace('.py', '')

        spec = importlib.util.spec_from_file_location(module_name, file)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        assert inspect.ismodule(module)
        assert inspect.getmembers(module, inspect.isclass)
        assert inspect.isclass(module.MockMLPlay)
        obj1 = module.MockMLPlay()
        obj2 = MockMLPlay()
        assert type(obj1).__name__ == type(obj2).__name__
        assert obj2.func() == obj1.func()

# if __name__ == '__main__':
#     # filename will be placed at first arg
#     cmd = "-i ./mock_included_file.py -i ./mock_included_file.py mygame --user 1 --map 2"
#     # sys.argv = cmd.split(" ")
#     cmd_parser = get_command_parser()
#     parsed_args = cmd_parser.parse_args(cmd.split())
#     print(parsed_args)

# parse args to get file
# file = parsed_args.input_script[0]
# print(file)

# import module
# module_name = os.path.basename(file)
# spec = importlib.util.spec_from_file_location(module_name, file)
# module = importlib.util.module_from_spec(spec)
# spec.loader.exec_module(module)
# print(module)
# assert "./mock_included_file.py" in parsed_args.input_script
