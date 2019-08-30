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

class TransitionProcessError(ProcessError):
    """
    Exception raised when an error occurred in the transition process
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
