# coding: utf-8
import os
import time
from multiprocessing import Pool, Manager
from log_test import init_log


def do_fun(que, index):
    if que.empty():
        return
    name = que.get_nowait()
    log = init_log("child:{}".format(index))
    pid = os.getpid()
    log.info("pid:{},child index:{},name:child-{}".format(pid, index, name))
    return


if __name__ == "__main__":
    name_list = ['aa', 'bb', 'cc', 'dd', 'ee',
                 'ff', 'gg', 'hh', 'jj', 'kk',
                 'll', 'mm', 'nn', 'oo', 'pp',
                 'qq', 'rr', 'ss', 'tt', 'uu']

    log = init_log("main")
    pool = Pool(processes=50)
    que = Manager().Queue(8000)
    start_time = time.time()
    for i in range(0, 160000):
        while que.full():
            time.sleep(20)
        log.debug("main index:{}".format(i))
        que.put_nowait(i)
        pool.apply_async(do_fun, (que, i, ))
    pool.close()
    pool.join()
    print '%d second' % (time.time() - start_time)
