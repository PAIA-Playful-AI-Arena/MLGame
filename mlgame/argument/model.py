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

    # def __init__(self,**kwargs):
    #     self.
    #     self.is_manual = self.ai_clients is None
    @validator('is_manual', always=True)
    def update_manual(cls, v, values) -> bool:
        if 'ai_clients' in values:
            return values['ai_clients'] is None
        return True


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
