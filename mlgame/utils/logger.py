import logging
from functools import cache

_logger = None


@cache
def get_singleton_logger():
    global _logger
    # TODO use arg to set debug level
    if _logger is None:
        logging.basicConfig(level=logging.WARNING)
        # logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(__file__)
        # console_handler = logging.StreamHandler(stream=sys.stdout)
        # console_handler.setLevel(level=logging.DEBUG)
        # logger.addHandler(console_handler)
        # logger.debug(" test debug")
    return _logger


logger = get_singleton_logger()
