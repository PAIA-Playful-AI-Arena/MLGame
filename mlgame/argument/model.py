import datetime
import os
from typing import Union, List, Optional

import pydantic
from pydantic import FilePath, validator, DirectoryPath
from pathlib import Path
from mlgame.utils.io import check_folder_existed_and_readable_or_create


class MLGameArgument(pydantic.BaseModel):
    """
    Data Entity to handle parsed cli arguments
    """
    fps: int = 30
    progress_frame_frequency: int = 300
    one_shot_mode: bool = False
    ai_clients: Optional[List[FilePath]] = None
    is_manual: bool = False
    no_display: bool = True
    ws_url: pydantic.AnyUrl = None
    game_folder: DirectoryPath
    game_params: List[str]
    output_folder: Union[Path, None] = None
    progress_folder: Union[Path, None] = None

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
        if check_folder_existed_and_readable_or_create(path):
            return path

    @validator('progress_folder')
    def update_progress_folder(cls, v, values):
        if v is None:
            return None
        path = os.path.join(
            str(v),
            datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        )
        if check_folder_existed_and_readable_or_create(path):
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
