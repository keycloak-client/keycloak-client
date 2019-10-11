# -*- coding: utf-8 -*-
import sys
import logging

from .constants import Logger


# define log formatter
log_format = "%(asctime)s [%(levelname)s] %(message)s"
formatter = logging.Formatter(log_format)


# define stream handler
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)


# define logger
logger = logging.getLogger(Logger.name)
logger.setLevel(logging.DEBUG)


# add handlers
logger.addHandler(stream_handler)
