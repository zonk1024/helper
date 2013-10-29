#!/usr/bin/env python


if __name__ == '__main__':
    import helper
    my_helper = helper.Helper()
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
    my_helper.info(helper.SETTINGS)
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
