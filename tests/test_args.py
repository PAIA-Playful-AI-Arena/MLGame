import importlib
import inspect
import os
import random

import pydantic

from tests.argument import MLGameArgument, get_parsed_args, create_MLGameArgument_obj
from tests.mock_included_file import MockMLPlay


def test_to_get_fps_and_one_shot_mode():
    fps = random.randint(10, 100)
    arg_str = f"-f {fps} " \
              " mygame --user 1 --map 2"
    parsed_args = get_parsed_args(arg_str)
    assert parsed_args.fps == fps
    assert not parsed_args.one_shot_mode

    arg_str = f"-1 " \
              " mygame --user 1 --map 2"
    parsed_args = get_parsed_args(arg_str)
    assert parsed_args.fps == 30
    assert parsed_args.one_shot_mode
    assert parsed_args.ai_clients is None
    # parse args to get file and import module class


def test_to_get_ai_module():
    arg_str = "-i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " mygame --user 1 --map 2"
    parsed_args = get_parsed_args(arg_str)
    assert parsed_args.ai_clients
    # parse args to get file and import module class
    for file in parsed_args.ai_clients:
        assert_contain_MockMLPlay(file)


def assert_contain_MockMLPlay(file):
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


def test_use_argument_model():
    arg_str = "-f 60 -1 -i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " ../games/easy_game --score 10 --color FF9800 --time_to_play 600 --total_point 50"
    arg_obj = create_MLGameArgument_obj(arg_str)
    assert arg_obj.one_shot_mode is True
    assert arg_obj.is_manual is False
    for file in arg_obj.ai_clients:
        assert_contain_MockMLPlay(file)

    arg_str = "-f 60 -1 -i ./mock_included_file.py -i ../tests/mock_included_file.py " \
              "--input-ai /Users/kylin/Documents/02-PAIA_Project/MLGame/tests/mock_included_file.py" \
              " ../games/easy_gam --score 10 --color FF9800 --time_to_play 600 --total_point 50"
    try:
        arg_obj = create_MLGameArgument_obj(arg_str)
        assert False
    except pydantic.ValidationError as e:
        print(e.__str__())
    # TODO parse game parameters

    # assert arg_obj.game_folder
    # assert arg_obj.game_folder

    pass
