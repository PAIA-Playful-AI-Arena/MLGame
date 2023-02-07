from mlgame.argument.cmd_argument import parse_cmd_and_get_arg_obj


def test_parse_output_folder_arg():
    arg_str = "-o /Users/kylin/Documents/02-PAIA_Project/MLGame/var -i /Users/kylin/Documents/02-PAIA_Project/MLGame/ai_clients/arkanoid/rule/ml_play.py /Users/kylin/Documents/02-PAIA_Project/MLGame/games/arkanoid "
    args = parse_cmd_and_get_arg_obj(arg_str.split(' '))

    assert "var" in str(args.output_folder)
