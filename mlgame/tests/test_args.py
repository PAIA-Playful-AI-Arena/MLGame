from os import path

from mlgame.argument.tool import read_json_file, parse_config


def test_read_config():
    config_file = path.join(path.dirname(__file__), "test_data", "game_config.json")
    config_data = read_json_file(config_file)
    assert config_data


def test_parse_config():
    config_file = path.join(path.dirname(__file__), "test_data", "game_config.json")
    config_data = read_json_file(config_file)
    params = config_data["game_params"]

    result = parse_config(config_data)
    assert result
    assert "()" in result
    for param in params:
        assert param["name"] in result
    print(result)
