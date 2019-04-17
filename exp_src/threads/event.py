# coding: utf-8

import time
from multiprocessing import Lock
from multiprocessing.pool import ThreadPool
import threading

import logging
from logging import getLogger, Formatter
from logging.handlers import RotatingFileHandler
import os


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.mkdir(directory)


def init_log(module_name, sub_name):
    log_dir = './logs'
    ensure_dir(log_dir)
    log_file = '%s/wxx_crawler_%s.log' % (log_dir, module_name.lower())
    rotate_handler = RotatingFileHandler(log_file, mode="a", encoding="utf-8", backupCount=3)
    date_fmt_str = '%Y-%m-%d %H:%M:%S'
    format_str = '[%(asctime)s][%(process)s][%(module)s:%(lineno)s %(funcName)s()][%(levelname)s] %(message)s'
    formatter = logging.Formatter(format_str, date_fmt_str)
    rotate_handler.setFormatter(formatter)
    logger = logging.getLogger(sub_name)
    if not logger.handlers:
        logger.addHandler(rotate_handler)
        logger.setLevel(logging.DEBUG)
    return logger


def save(data, logger):
    # lock.acquire()
    print("cc:{}".format(data))
    logger.info("cc:{}".format(data))
    # lock.release()


def worker(num, logger):
    time.sleep(2)
    save(num, logger)


if __name__ == "__main__":
    w_start = time.time()
    pool = ThreadPool(processes=100)  # 参数是线程池的数量，默认为1
    logger_out = init_log("wxx", "test")
    count = 0
    while 1:
        count += 1
        for i in range(10):
            pool.apply_async(func=worker, args=(i + count, logger_out))
        if count < 100:
            continue
        else:
            break
    pool.close()  # 关闭线程池 不再提交任务
    pool.join()  # 等待线程池里面的任务执行完毕
    print(time.time() - w_start)
