### 多进程条件下的python日志打印问题
- 办法
> pip install ConcurrentLogHandler

> wget https://pypi.python.org/packages/fd/e5/0dc4f256bcc6484d454006b02f33263b20f762a433741b29d53875e0d763/ConcurrentLogHandler-0.9.1.tar.gz#md5=9609ecc4c269ac43f0837d89f12554c3

> cd ConcurrentLogHandler-0.9.1

> python2.7 setup.py install

```python
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

```
