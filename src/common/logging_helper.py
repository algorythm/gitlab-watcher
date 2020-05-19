from __future__ import annotations
import logging, coloredlogs

def get_logger(context: str, log_dir = '/tmp/gitlab_watcher', min_level='DEBUG') -> logging.Logger:
    logger = logging.getLogger(context)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(log_dir)
    console_handler = logging.StreamHandler()

    log_format = '%(asctime)s [%(name)s::%(levelname)s]: %(message)s'

    file_handler.setFormatter(logging.Formatter(log_format))
    file_handler.setLevel(level=logging.DEBUG)
    coloredlogs.DEFAULT_FIELD_STYLES['levelname']['color'] = 'white'
    console_handler.setFormatter(coloredlogs.ColoredFormatter(log_format))
    console_handler.setLevel(level=logging.DEBUG)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
