from loguru import logger


try:
    x = 0

    10 / x
except Exception as e:
    logger.exception(e)

