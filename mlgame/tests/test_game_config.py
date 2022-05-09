from mlgame.argument.model import GameConfig


def test_create_game_config():
    game_folder = "/Users/kylin/Documents/02-PAIA_Project/MLGame/games/easy_game"
    game_config = GameConfig(game_folder=game_folder)
    # game_config.config_to_create_parser
    assert hasattr(game_config,'config_to_create_parser')
    assert hasattr(game_config,'game_version')
    assert hasattr(game_config,'game_cls')
