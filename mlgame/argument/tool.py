import json
import logging

import pydantic
from pydantic import validator


def get_data_from_json_file(file_path) -> dict:
    """
    open json file and return dict data
    """
    with open(file=file_path, mode="rb") as f:
        config_data = json.load(f)
    return config_data


class UserNumConfig(pydantic.BaseModel):
    min: int
    max: int

    @validator('max')
    def max_should_be_larger_than_min(cls, v, values):
        assert v >= values['min']
        return v

def revise_ai_clients(ai_clients: list, user_num_config: UserNumConfig):
    ai_clients_result = ai_clients.copy()
    if len(ai_clients) < user_num_config.min:
        logging.warning("提供的ＡＩ數量小於遊戲最小所需ＡＩ數量，系統將會使用最後一個ＡＩ自動補足")
        while len(ai_clients_result) < user_num_config.min:
            ai_clients_result.append(ai_clients[-1])
    elif len(ai_clients) > user_num_config.max:
        logging.warning("提供的ＡＩ數量高過遊戲容許範圍，系統將會忽略倒數幾個ＡＩ")
        ai_clients_result = ai_clients[:user_num_config.max]
    return ai_clients_result
