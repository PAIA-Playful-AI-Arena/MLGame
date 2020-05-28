import sys

from mlgame.transition import TransitionManager

if __name__ == "__main__":
    server_info = sys.argv[1].split('=')[-1].split(':')
    error_message = sys.argv[2]

    server = TransitionManager(lambda x: None, server_info)
    server.send_start_error(error_message)
