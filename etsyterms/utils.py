import logging
import os


def setup_logging(log_level: str = None):
    if not log_level:
        log_level = os.environ.get('LOG_LEVEL', 'ERROR')

    numeric_level = getattr(logging, log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {log_level}')

    logging.basicConfig(format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s', level=numeric_level)
