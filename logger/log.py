"""
Logging.
"""

# System imports
import logging
from logging.config import fileConfig
from os import path


def config() -> None:
    """
    Description
    --
    Loads the logging configuration.
    """

    log_file_path = path.join(path.dirname(path.abspath(__file__)), 'log.ini')
    fileConfig(log_file_path)


def get_module_logger(mod_name: str) -> logging.Logger:
    """
    Description
    --
    Gets a logger for the module.

    Parameters
    -- mod_name - the module name.
    """

    if not mod_name:
        raise ValueError("mod_name is required!")

    logger = logging.getLogger(mod_name)

    # TODO: Create logs dir?
    # os.makedirs(os.path.dirname(full_path), exist_ok=True)

    return logger
