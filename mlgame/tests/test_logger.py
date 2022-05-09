import logging

from mlgame.utils.logger import get_singleton_logger


def test_get_single_logger():
    logger = get_singleton_logger()
    assert isinstance(logger,logging.Logger)

    # logger.debug("debug fadsfasdf")