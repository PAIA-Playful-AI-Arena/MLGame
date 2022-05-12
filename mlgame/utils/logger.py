import logging
from functools import cache

_logger = None


@cache
def get_singleton_logger():
    global _logger
    if _logger is None:
        _logger = logging.getLogger(__file__)
    return _logger


logger = get_singleton_logger()
