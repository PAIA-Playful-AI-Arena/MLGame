from mlgame.argument.tool import revise_ai_clients, UserNumConfig


def test_revise_ai_clients():
    ai_client_files = ['./1p.py', './2p.py']

    """
        輸入兩個AI 遊戲允許最多兩個AI
    """
    user_num_config = UserNumConfig(min=1, max=2)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == 2

    """
        輸入兩個AI 遊戲允許最多四個AI
    """
    user_num_config = UserNumConfig(min=1, max=4)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == 2

    """
        輸入兩個AI 遊戲允許最多一個AI，系統會去掉最後一個
    """
    user_num_config = UserNumConfig(min=1, max=1)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == user_num_config.max
    assert ai_client_files[0] in ai_clients

    """
        輸入一個AI 遊戲允許最少需要兩個AI，系統會補上一個
    """
    ai_client_files = ['./1p.py']
    user_num_config = UserNumConfig(min=2, max=2)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == user_num_config.min
    assert ai_client_files[0] == ai_clients[0] == ai_clients[1]

    """
            輸入一個AI 遊戲允許最少需要四個AI，系統會補上三個
    """
    ai_client_files = ['./1p.py']
    user_num_config = UserNumConfig(min=4, max=4)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == user_num_config.min
    assert ai_client_files[0] == ai_clients[0] == ai_clients[1]

    """
            輸入兩個AI 遊戲允許最少需要四個AI，系統會用最後一個補上兩個
    """
    ai_client_files = ['./1p.py','./2p.py']
    user_num_config = UserNumConfig(min=4, max=4)
    ai_clients = revise_ai_clients(ai_client_files, user_num_config=user_num_config)
    assert len(ai_clients) == user_num_config.min
    assert ai_client_files[1] == ai_clients[-1]