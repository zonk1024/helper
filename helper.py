#!/usr/bin/env python

import os
import sys


SETTINGS = {}
try:
    from env_settings import SETTINGS
except ImportError:
    pass
HOME_DIR = os.getenv('HOME')
PROJECT_DIR = SETTINGS.get('project_dir', '{}/projects'.format(HOME_DIR))
LOG_DIR = SETTINGS.get('log_dir', '{}/log'.format(HOME_DIR))
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

import logging
import optparse


def find_main_file_base():
    """
    Returns PYTHON_SHELL if there is no __file__ for __main__
    """
    if hasattr(sys.modules['__main__'], '__file__'):
        return os.path.split(sys.modules['__main__'].__file__)[1].rstrip('.py')
    return 'PYTHON_SHELL'

def mkdir(dirname):
    """
    Works like -p
    """
    base_dir, actual_dir = os.path.split(dirname)
    if actual_dir:
        mkdir(base_dir)
    if not os.path.isdir(dirname):
        os.mkdir(dirname)

class Helper(object):
    """
    Helper class which combines the logger and option parser
    """
    LOG_FILE = '{}/{}.log'.format(LOG_DIR, find_main_file_base())
    LOG_LEVEL = logging.INFO
    def __init__(self):
        self.build_option_parser()
        self.build_options()
        self.initialize_logger()
        self.setup_logger()

    # Parser functions
    def build_option_parser(self):
        """
        Function to initially build parser
        """
        self.option_usage = 'usage: %prog [options] args'
        self.option_parser = optparse.OptionParser(self.option_usage)
        self.option_logger_group = optparse.OptionGroup(self.option_parser, 'Logging Options', 'Helper\'s builtin logging options')
        self.option_logger_group.add_option('-l', '--log_stdout', action='store_false', default='true', help='Toggle off logging to stdout')
        self.option_logger_group.add_option('-L', '--log_file', action='callback', callback=self.log_file_callback, dest='log_file', default=None, help='Logs to given file, none if missing, or {} if naked'.format(self.LOG_FILE))
        self.option_logger_group.add_option('-v', '--verbose', action='count', default=0, help='Increase logging [may pass multiple]')
        self.option_logger_group.add_option('-q', '--quiet', action='store_const', const=-1, help='Decrease logging level to none', dest='verbose')
        self.option_parser.add_option_group(self.option_logger_group)

    def build_options(self):
        """
        Called to [re-]build options and args
        """
        self.options, self.args = self.option_parser.parse_args()

    def add_option(self, *args, **kwargs):
        """
        Wrapper to add options to the parser
        """
        self.option_parser.add_option(*args, **kwargs)
        self.build_options()

    def log_file_callback(self, option, opt_string, value, parser, args=[], kwargs={}):
        if value is None:
            setattr(parser.values, option.dest, self.log_file)
            return self.log_file
        setattr(parser.values, option.dest, value)
        return value

    # Logging functions
    def build_log_string(self):
        output =  '[%(asctime)s] '
        output += '[%(name)s:%(lineno)d] '
        if 'multiprocessing' in globals() or 'subprocess' in globals():
            output += '[PID:%(process)s] '
        if 'threading' in globals():
            output += '[Thread:%(thread)s] '
        output += '[%(levelname)s] '
        output += '%(message)s'
        return output

    def log_level_from_options(self):
        if self.options.verbose is 0:
            return self.LOG_LEVEL
        return min(60, max(0, 50 - (self.options.verbose * 10)))

    def initialize_logger(self):
        self.null_handler = None
        self.stream_handler = None
        self.file_handler = None
        self.log_level = self.log_level_from_options()
        self.log_file = self.LOG_FILE

    def setup_logger(self):
        self.log_formatter = logging.Formatter(self.build_log_string())
        self.logger = logging.getLogger(find_main_file_base())
        self.log_level = self.log_level_from_options()
        self.logger.setLevel(self.log_level)

        if self.null_handler is None:
            self.null_handler = logging.NullHandler()
            self.logger.addHandler(self.null_handler)

        if self.options.log_stdout and self.stream_handler is None:
            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setLevel(self.log_level)
            self.stream_handler.setFormatter(self.log_formatter)
            self.logger.addHandler(self.stream_handler)
        elif self.stream_handler is not None:
            self.stream_handler.setFormatter(self.log_formatter)

        if self.options.log_file and self.file_handler is None:
            mkdir(LOG_DIR)
            self.file_handler = logging.FileHandler(self.log_file)
            self.file_handler.setLevel(self.log_level)
            self.file_handler.setFormatter(self.log_formatter)
            self.logger.addHandler(self.file_handler)
        elif self.file_handler is not None:
            self.file_handler.setFormatter(self.log_formatter)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)

    def exception(self, msg):
        self.logger.exception(msg)

    def critical(self, msg):
        self.logger.exception(msg)

if __name__ == '__main__':
    my_helper = Helper()
    my_helper.info('This is an info.')
    import threading
    my_helper.setup_logger()
    my_helper.info('This is an info.')
    import multiprocessing
    my_helper.setup_logger()
    my_helper.info('This is an info.')
    del(threading)
    my_helper.setup_logger()
    my_helper.info('This is an info.')
    del(multiprocessing)
    my_helper.setup_logger()
    my_helper.info('This is an info.')
    my_helper.info('Settings: {}'.format(SETTINGS))
    my_helper.info('Options: {}'.format(my_helper.options))
    my_helper.debug('This is a debug.')
    my_helper.info('This is an info.')
    my_helper.warning('This is a warning.')
    my_helper.error('This is an error.')
    try:
        no_way = 1/0
    except Exception:
        my_helper.exception('This is an exception.')
    try:
        no_way = 1/0
    except Exception:
        my_helper.critical('This is a critical.')
    my_helper.info('This is an info.')
