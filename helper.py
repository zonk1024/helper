#!/usr/bin/env python

import os
HOME_DIR = os.getenv('HOME')
PROJECT_DIR = '{}/projects'.format(HOME_DIR)
LOG_DIR = '{}/log'.format(HOME_DIR)

import sys
if PROJECT_DIR not in sys.path:
    sys.path.append(PROJECT_DIR)

import logging
import optparse

class Helper(object):
    def __init__(self):
        try:
            import env_settings
            self.env_settings = env_settings.settings
            del(env_settings)
        except ImportError:
            pass
        self.log_level = logging.INFO
        self.null_handler = None
        self.stream_handler = None
        self.file_handler = None
        self.stdout = True
        self.to_file = True
        self.option_usage = 'usage: %prog [options] args'
        self.main_file_base = self.find_main_file_base()
        self.log_file = '{}/{}.log'.format(LOG_DIR, self.main_file_base)

        self.option_parser = optparse.OptionParser(self.option_usage)
        self.option_logger_group = optparse.OptionGroup(self.option_parser, 'Logging Commands')
        self.option_logger_group.add_option('-l', '--log_stdout', action='store_false', default='true', help='Disable logging to stdout')
        self.option_logger_group.add_option('-L', '--log_file', action='callback', callback=self.log_file_callback, dest='log_file', default=None, help='Logs to given file, else if naked:\n{}'.format(self.log_file))
        self.option_logger_group.add_option('-v', '--verbose', action='count', default=0, help='Verbose [may pass multiple]')
        self.option_logger_group.add_option('-q', '--quiet', action='store_const', const=-1, help='Disable logging to stdout', dest='verbose')
        self.option_parser.add_option_group(self.option_logger_group)

        self.build_options()
        self.setup_logger()

    def find_main_file_base(self):
        """
        Logfile is PYTHON_SHELL if there is no __file__ for __main__
        """
        if hasattr(sys.modules['__main__'], '__file__'):
            return os.path.split(sys.modules['__main__'].__file__)[1].rstrip('.py')
        return 'PYTHON_SHELL'

    # Parser functions
    def add_option(self):
        self.build_options()

    def build_options(self):
        """
        Called to [re-]build options and args
        """
        self.options, self.args = self.option_parser.parse_args()

    def log_file_callback(self, option, opt_string, value, parser, args=[], kwargs={}):
        if value is None:
            setattr(parser.values, option.dest, self.log_file)
            return self.log_file
        setattr(parser.values, option.dest, value)
        return value

    # Util functions
    @classmethod
    def mkdir(cls, dirname):
        """
        Works like -p
        """
        base_dir, actual_dir = os.path.split(dirname)
        if actual_dir:
            cls.mkdir(base_dir)
        if not os.path.isdir(dirname):
            os.mkdir(dirname)

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
        #print 'build_log_string returning {}'.format(output)
        return output

    def setup_logger(self):
        self.log_formatter = logging.Formatter(self.build_log_string())
        self.logger = logging.getLogger(self.main_file_base)
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
            self.mkdir(LOG_DIR)
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
    helper = Helper()
    helper.info('This is a info.')
    import threading
    helper.setup_logger()
    helper.info('This is a info.')
    import multiprocessing
    helper.setup_logger()
    helper.info('This is a info.')
    del(threading)
    helper.setup_logger()
    helper.info('This is a info.')
    del(multiprocessing)
    helper.setup_logger()
    helper.info('This is a info.')
    print helper.env_settings
    #helper.debug('This is a debug.')
    #helper.info('This is a info.')
    #helper.warning('This is a warning.')
    #helper.error('This is a error.')
    #helper.exception('This is a exception.')
    #helper.critical('This is a critical.')
