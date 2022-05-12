from mlgame.view.decorator import check_scene_init_data, check_game_progress
from mlgame.view.view_model import get_scene_init_sample_data, get_dummy_progress_data


@check_scene_init_data
def example_of_use_init_decorator():
    """
    add @check_init_data will check the returned result of this function
    if you want to validate your init data, you could add this decorator easily to check
    :return:
    """
    # collect your init data here
    result = get_scene_init_sample_data()
    return result


@check_game_progress
def example_of_use_progress_decorator():
    """
    add @check_init_data will check the returned result of this function
    if you want to validate your init data, you could add this decorator easily to check
    :return:
    """
    # collect your init data here
    result = get_dummy_progress_data()
    return result


def test_example():
    example_of_use_init_decorator()
    example_of_use_progress_decorator()
