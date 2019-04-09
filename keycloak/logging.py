#! -*- coding: utf-8 -*-

""" This mixin takes care of all functionalities associated with logging """

import os
import logging
from logging.handlers import RotatingFileHandler

from cached_property import cached_property


# pylint: disable=too-few-public-methods
class LoggingMixin:
    """ Logging mixin to handle logging related functionalities """

    def __init__(self, log_dir=None, log_level=logging.DEBUG, **kwargs):
        """ initialize the logging parameters """

        # define log directory
        self.log_dir = log_dir or '/tmp'

        # create logger
        self.log = logging.getLogger('keycloak')
        self.log.setLevel(log_level)

        # attach handlers to the logger
        for handler in self.handlers:
            self.log.addHandler(handler)

        super(LoggingMixin, self).__init__(**kwargs)

    @cached_property
    def log_file(self):
        """ log file """
        return os.path.join(self.log_dir, 'keycloak.log')

    @cached_property
    def format(self):
        """ log format """
        return logging.Formatter('%(levelname)s - %(asctime)s - %(filename)s:%(lineno)d - %(message)s')

    @cached_property
    def handlers(self):
        """ log handlers """
        file_handler = RotatingFileHandler(filename=self.log_file, maxBytes=10000000, backupCount=5)
        file_handler.setFormatter(self.format)
        return (file_handler,)
