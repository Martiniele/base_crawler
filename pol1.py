import time
import json

def sayhello(str):
    print "Hello ", str
    time.sleep(2)


if __name__ == "__main__":
    name_list = ['xiaozi', 'aa', 'bb', 'cc''xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa', 'bb', 'xiaozi', 'aa']
    start_time = time.time()
    for i in range(len(name_list)):
        sayhello(name_list[i])
    print '%d second' % (time.time() - start_time)
