# coding: utf-8


from multiprocessing import Pipe, Pool, Process, Manager, Lock
import os
import time


def do(que, x, pi):
    print("cur:{}, child:{}".format(que.get(), os.getpid()))
    time.sleep(3)
    pi.send("{}finish".format(x))


if __name__ == "__main__":
    pool = Pool(processes=10)
    que = Manager().Queue(maxsize=10)
    pipe = Pipe(duplex=True)
    print("parent:{}".format(os.getpid()))
    for i in range(1, 100, 1):
        while que.full():
            print("full...")
            time.sleep(2)
        que.put(i)
        pool.apply_async(do, (que, i, pipe[0]))

    print("main pi:{}".format(pipe[1].recv()))
    pool.close()
    pool.join()