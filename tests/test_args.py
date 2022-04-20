import argparse
import importlib
import os
import sys
from argparse import ArgumentParser, REMAINDER

version = "9.3.5"


def validate_file(f):
    if not os.path.exists(f):
        # Argparse uses the ArgumentTypeError to give a rejection message like:
        # error: argument input: x does not exist
        raise argparse.ArgumentTypeError("{0} does not exist".format(f))
    return f


def get_command_parser():
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
    # group.add_argument("-l", "--list", action="store_true", dest="list_games",
    #                    help="list available games. If the game in the 'games' directory "
    #                         "provides 'config.py' which can be loaded, it will be listed.")

    group = parser.add_argument_group(title="game execution options",
                                      description="Game execution options must be specified before <game> arguments.")
    # group.add_argument("-f", "--fps", type=int, default=30,
    #                    help="the updating frequency of the game process [default: %(default)s]")
    # group.add_argument("-m", "--manual-mode", action="store_true",
    #                    help="start the game in the manual mode instead of "
    #                         "the machine learning mode [default: %(default)s]")
    # group.add_argument("-r", "--record", action="store_true", dest="record_progress",
    #                    help="pickle the game progress (a list of SceneInfo) to the log file. "
    #                         "One file for a round, and stored in '<game>/log/' directory. "
    #                         "[default: %(default)s]")
    # group.add_argument("-1", "--one-shot", action="store_true", dest="one_shot_mode",
    #                    help="quit the game when the game is passed or is over. "
    #                         "Otherwise, the game will restart automatically. [default: %(default)s]")

    group.add_argument("-i", "--input-script",
                       # type=validate_file,
                       type=os.path.abspath,
                       action="append",
                       default=None, metavar="SCRIPT",
                       help="specify user script(s) for the machine learning mode. "
                            "For multiple user scripts, use this flag multiple times. "
                            "The script path starts from 'games/<game_name>/ml/' directory. "
                            "'-i ml_play.py' means the script path is 'games/<game_name>/ml/ml_play.py', and "
                            "'-i foo/ml_play.py' means the script path is 'games<game_name>/ml/foo/ml_play.py'. "
                            "If the script is in the subdirectory of the 'ml' directory, make sure the "
                            "subdirectory has '__init__.py' file.")

    return parser


if __name__ == '__main__':
    print(sys.argv)
    # filename will be placed at first arg
    assert "test_args.py" in sys.argv[0]

    cmd_parser = get_command_parser()
    parsed_args = cmd_parser.parse_args()
    # print(parsed_args)

    # parse args to get file
    file = parsed_args.input_script[0]
    # print(file)

    # import module
    module_name = os.path.basename(file)
    spec = importlib.util.spec_from_file_location(module_name, file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    print(module)
    # assert "./mock_included_file.py" in parsed_args.input_script
