import logging
import sys
from functools import cache

_logger = None


@cache
def get_singleton_logger():
    global _logger
    if _logger is None:
        logging.basicConfig(level=logging.DEBUG)
        _logger = logging.getLogger(__file__)
        # console_handler = logging.StreamHandler(stream=sys.stdout)
        # console_handler.setLevel(level=logging.DEBUG)
        # logger.addHandler(console_handler)
        # logger.debug(" test debug")
    return _logger
