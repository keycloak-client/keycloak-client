#! -*- coding: utf-8 -*-

""" This module takes care of all functionalities associated with logging """

import os
import logging
from logging.handlers import RotatingFileHandler


def get_formatter():
    """
    Method to construct log formatter
    """
    return logging.Formatter(
        "%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s"
    )


def get_file_handler(log_dir=None):
    """
    Method to construct file handler

    Args:
        log_dir (str): directory to write logs
    """

    # log file
    log_dir = log_dir or os.getcwd()
    log_file = os.path.join(log_dir, "keycloak.log")

    # formatter
    formatter = get_formatter()

    # handler
    file_handler = RotatingFileHandler(
        filename=log_file, maxBytes=10000000, backupCount=5
    )
    file_handler.setFormatter(formatter)

    return file_handler


def get_logger(log_dir=None, log_level=logging.INFO):
    """
    Method to construct logger

    Args:
        log_dir (str): directory to write logs
        log_level (str): logging level
    """

    # handler
    file_handler = get_file_handler(log_dir)

    # create logger
    logger = logging.getLogger("keycloak")
    logger.setLevel(log_level)
    logger.addHandler(file_handler)

    return logger
