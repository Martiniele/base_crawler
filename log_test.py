import logging
from logging import getLogger, Formatter
from cloghandler import ConcurrentRotatingFileHandler


def init_log(name):
    logfile = "./log/restful_api_thread.log"
    filesize = 800 * 1024 * 1024
    log = getLogger(name)
    rotate_handler = ConcurrentRotatingFileHandler(logfile, "a", filesize, encoding="utf-8")

    datefmt_str = '%Y-%m-%d %H:%M:%S'
    format_str = '[%(asctime)s][%(levelname)s] %(message)s'
    formatter = Formatter(format_str, datefmt_str)
    rotate_handler.setFormatter(formatter)

    log.addHandler(rotate_handler)
    log.setLevel(logging.DEBUG)
    return log
