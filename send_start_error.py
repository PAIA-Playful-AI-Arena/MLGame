import sys

from mlgame.transition import TransitionManager

if __name__ == "__main__":
    server_info = sys.argv[1].split('=')[-1].split(':')

    message_list = sys.argv[2].splitlines(keepends = True)
    for line in message_list:
        if "Error" in line or "error" in line:
            error_message = line
            break

    server = TransitionManager(lambda x: None, server_info)
    server.send_start_error(error_message)
