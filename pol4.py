# coding: utf-8
import os
import time
from multiprocessing import Pool, Manager
from log_test import init_log


def do_fun(que, index):
    if que.empty():
        return
    name_list = que.get()
    log = init_log("child")
    pid = os.getpid()
    for name in name_list:
        log.info("pid:{},child index:{},name:{}".format(pid, index, name))
    return


if __name__ == "__main__":
    name_list = ['aa', 'bb', 'cc', 'dd', 'ee',
                 'ff', 'gg', 'hh', 'jj', 'kk',
                 'll', 'mm', 'nn', 'oo', 'pp',
                 'qq', 'rr', 'ss', 'tt', 'uu']

    log = init_log("main")
    pool = Pool(processes=20)
    que = Manager().Queue(20)
    start_time = time.time()
    for i in range(0, 20):
        while que.full():
            time.sleep(20)
        log.debug("main index:{}".format(i))
        que.put(name_list)
        pool.apply_async(do_fun, (que, i, ))
    pool.close()
    pool.join()
    print '%d second' % (time.time() - start_time)
