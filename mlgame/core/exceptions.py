import datetime
import json
from enum import Enum, auto

import pydantic as pydantic


class ProcessError(Exception):
    """
    The base class for the exception occurred in the process
    """

    def __init__(self, process_name, message):
        """
        Constructor

        @param process_name The name of the process in which the error occurred
        @param message The error message
        """
        self.process_name = process_name
        self.message = message

class GameProcessError(ProcessError):
    """
    Exception raised when an error occurred in the game process
    """
    pass

class MLProcessError(ProcessError):
    """
    Exception raised when an error occurred in the ml process
    """
    pass

def trim_callstack(exception_msg: str, target_user_file: str):
    """
    Shorten the call stack to the starting point of the user script
    """
    exception_msg_list = exception_msg.splitlines(keepends = True)
    # Store title
    trimmed_msg = exception_msg_list[0]

    # Find the starting point
    i = 0
    for i in range(2, len(exception_msg_list)):
        if target_user_file in exception_msg_list[i]:
            break

    return trimmed_msg + "".join(exception_msg_list[i:])

class ExecutionCommandError(Exception):
    """
    Exception raised when parsed invalid execution command
    """
    def __init__(self, message):
        """
        Constructor
        """
        self.message = message

    def __str__(self):
        return self.message

class GameConfigError(Exception):
    """
    Exception raised when the game provides invalid game config
    """
    def __init__(self, message):
        """
        Constructor
        """
        self.message = message

    def __str__(self):
        return self.message


class ErrorEnum(str, Enum):
    AI_INIT_ERROR = auto()
    AI_EXEC_ERROR = auto()
    GAME_EXEC_ERROR = auto()
    COMMAND_ERROR = auto()


class GameError(pydantic.BaseModel):
    error_type: ErrorEnum
    message: str = ""
    frame: int
    time_stamp: datetime.datetime = datetime.datetime.now(datetime.timezone.utc)

    def data(self):
        data = {
            "type": "game_error",
            "data": {
                "error_type": self.error_type.name,
                "frame": self.frame,
                "message": self.message,
                "time_stamp": self.time_stamp.isoformat()
            }
        }
        return json.dumps(data)
