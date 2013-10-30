#!/usr/bin/env python

"""
Variable precedence:
    default -> config in SETTINGS -> cli args
"""

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
DEV_NULL = open('/dev/null', 'w')

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
    STREAM_MAP = {'stderr': sys.stderr, 'stdout': sys.stdout, 'none': DEV_NULL, '': DEV_NULL}
    def __init__(self):
        """
        It's init...
        """
        self.build_option_parser()

    def ready(self):
        """
        Called when all options have been added
        """
        self.build_options()
        self.initialize_logger()
        self.setup_logger()
        self.build_logging_wrappers()
        self.logger.info('Helper ready!')

    # Parser functions
    def build_option_parser(self):
        """
        Function to initially build parser
        """
        spaces = ''.join(' ' for _ in range(80))
        self.option_usage = 'usage: %prog [options] args'
        self.option_parser = optparse.OptionParser(self.option_usage)
        self.option_logger_group = optparse.OptionGroup(
            self.option_parser,
            'Logging Options',
            'Helper\'s builtin logging options',
        )
        self.option_logger_group.add_option(
            '--log-stream',
            dest='log_stream',
            action='store',
            default='stdout',
            type='str',
            help='Default: stdout{}Options: stderr or none'.format(spaces),
        )
        self.option_logger_group.add_option(
            '--log-file',
            action='store',
            dest='log_file',
            default=self.LOG_FILE,
            type='str',
            help='Default: {}{}Options: <Filename> or none.'.format(self.LOG_FILE, spaces),
        )
        self.option_logger_group.add_option(
            '-v',
            '--verbose',
            action='count',
            default=0,
            help='Increase logging [may pass multiple]',
        )
        self.option_logger_group.add_option(
            '-q',
            '--quiet',
            action='store_const',
            const=-1,
            help='Decrease logging level to none',
            dest='verbose',
        )
        self.option_parser.add_option_group(self.option_logger_group)

    def add_option(self, *args, **kwargs):
        """
        Wrapper to add options to the parser
        """
        self.option_parser.add_option(*args, **kwargs)

    def build_options(self):
        """
        Called to build options and args
        """
        self.options, self.args = self.option_parser.parse_args()

    # Logging functions
    def initialize_logger(self):
        """
        Initializes the one-time vars for the logger
        """
        self.null_handler = None
        self.stream_handler = None
        self.file_handler = None
        self.log_level = self.LOG_LEVEL
        self.log_file = self.LOG_FILE

    def setup_logger(self):
        """
        Ensures handlers are attached and resets some vars
        """
        self.log_formatter = logging.Formatter(self.build_log_string())
        self.logger = logging.getLogger(find_main_file_base())
        self.log_level = self.log_level_from_options()
        self.log_file = self.log_file_from_options()
        self.logger.setLevel(self.log_level)

        if self.null_handler is None:
            self.null_handler = logging.NullHandler()
        self.logger.addHandler(self.null_handler)

        if self.options.log_stream and self.stream_handler is None:
            self.stream_handler = logging.StreamHandler(stream=self.STREAM_MAP.get(self.options.log_stream.lower(), sys.stdout))
            self.logger.addHandler(self.stream_handler)
        if self.stream_handler:
            self.stream_handler.setLevel(self.log_level)
            self.stream_handler.setFormatter(self.log_formatter)

        if self.options.log_file and self.file_handler is None:
            mkdir(LOG_DIR)
            self.file_handler = logging.FileHandler(self.log_file)
            self.logger.addHandler(self.file_handler)
        if self.file_handler:
            self.file_handler.setLevel(self.log_level)
            self.file_handler.setFormatter(self.log_formatter)

    def build_logging_wrappers(self):
        """
        Pretty simple...
        """
        self.debug = self.logger.debug
        self.info = self.logger.info
        self.warning = self.logger.warning
        self.error = self.logger.error
        self.exception = self.logger.exception
        self.critical = self.logger.critical

    def build_log_string(self):
        """
        Function to build the log format string.
        Checks for multiprocessing, subprocess, and threading.
        """
        output =  '[%(asctime)s] '
        output += '[%(module)s:%(lineno)d] '
        if 'multiprocessing' in globals() or 'subprocess' in globals():
            output += '[PID:%(process)s] '
        if 'threading' in globals():
            output += '[Thread:%(thread)s] '
        output += '[%(levelname)s] '
        output += '%(message)s'
        return output

    def log_level_from_options(self):
        """
        Determines the log level based on the options passed
        """
        if self.options.verbose is 0:
            return self.log_level
        if self.options.verbose is -1:
            return 70
        # -qv = logging.CRITICAL, then each v goes up a level
        self.log_level = max(0, 70 - (self.options.verbose * 10))
        return self.log_level

    def log_file_from_options(self):
        """
        Determines the log level based on the options passed
        """
        if self.options.log_file is '':
            return None
        if self.options.log_file is None:
            return self.log_file
        return self.options.log_file
