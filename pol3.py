import time
from multiprocessing import Pool

import threadpool


def sayhello(str):
    print "Hello ", str
    time.sleep(20)


if __name__ == "__main__":
    name_list = ['xiaozi', 'aa', 'bb', 'cc''xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa',
                 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb']
    start_time = time.time()
    pool = Pool(processes=200)
    for i in name_list:
        pool.apply_async(sayhello, (i, ))
    pool.close()
    pool.join()
    print '%d second' % (time.time() - start_time)
