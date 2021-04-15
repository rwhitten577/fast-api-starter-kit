import logging.config
import os
from typing import Optional, Dict


def init_logging(*, env: str = os.getenv("PROJECT_ENV", "local"), root_level: Optional[str] = os.getenv("ROOT_LOG_LEVEL"),
                 disable_existing_loggers: bool = False, loggers: Optional[Dict[str, str]] = None,
                 is_lambda: bool = False):
    config = LOGGING_CONFIG
    config["disable_existing_loggers"] = disable_existing_loggers

    if root_level and root_level in LEVELS:
        log_level = root_level
    elif root_level and root_level not in LEVELS:
        raise Exception(f"Invalid root log level: {root_level}")
    else:
        if env in {"local", "dev"}:
            log_level = "DEBUG"
        else:
            log_level = "INFO"

    config["loggers"][""]["level"] = log_level

    if loggers:
        for module, level in loggers.items():
            if level not in LEVELS:
                raise Exception(f"Invalid log level for module {module}: {level}")

            config["loggers"][module] = {
                'handlers': ['default'],
                'level': level,
                'propagate': False
            }

    if is_lambda and env != "local":
        # Lambda runtime controls logging and sets handler, so we only need to set level.
        logging.getLogger().setLevel(log_level)
    else:
        logging.config.dictConfig(config)


LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)-15s|%(levelname)s|%(name)s|%(filename)s:%(lineno)s|%(funcName)s()|%(message)s'
        },
    },
    'handlers': {
        'default': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',  # Default is stderr
        },
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['default'],
            'level': 'DEBUG',
            'propagate': False
        },
        'boto3': {  # example of another package where you want to hardcode the level for all envs
            'handlers': ['default'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
