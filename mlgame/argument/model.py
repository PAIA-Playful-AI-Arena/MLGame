import datetime
import os
from typing import List, Optional

import pydantic
from pydantic import FilePath, validator, DirectoryPath


class MLGameArgument(pydantic.BaseModel):
    """
    Data Entity to handle parsed cli arguments
    """
    fps: int = 30
    one_shot_mode: bool = False
    ai_clients: Optional[List[FilePath]] = None
    is_manual: bool = False
    no_display: bool = True
    ws_url: pydantic.AnyUrl = None
    game_folder: DirectoryPath
    game_params: List[str]
    output_folder: pydantic.DirectoryPath = None

    # def __init__(self,**kwargs):
    #     self.
    #     self.is_manual = self.ai_clients is None
    @validator('is_manual', always=True)
    def update_manual(cls, v, values) -> bool:
        if 'ai_clients' in values:
            return values['ai_clients'] is None
        return True

    @validator('output_folder')
    def update_output_folder(cls, v, values):
        if v is None:
            return None
        path = os.path.join(
            str(v),
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        )
        if not os.path.exists(path):
            os.makedirs(path)

        if os.path.isdir(path) and os.access(path, os.R_OK):
            print(f'{path} is a readable directory')
        else:
            print(f'{path} is not a readable directory or does not exist')
        return path


class UserNumConfig(pydantic.BaseModel):
    """
    Data Entity to handle user_num in game_config.json
    """
    min: int
    max: int

    @validator('max')
    def max_should_be_larger_than_min(cls, v, values):
        assert v >= values['min']
        return v
