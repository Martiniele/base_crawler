### 多进程条件下的python日志打印问题
- 办法
> pip install ConcurrentLogHandler  #仅支持Linux环境

> wget https://pypi.python.org/packages/fd/e5/0dc4f256bcc6484d454006b02f33263b20f762a433741b29d53875e0d763/ConcurrentLogHandler-0.9.1.tar.gz#md5=9609ecc4c269ac43f0837d89f12554c3

> cd ConcurrentLogHandler-0.9.1

> python2.7 setup.py install

```python
import logging
from logging import getLogger, Formatter
from cloghandler import ConcurrentRotatingFileHandler


def init_log(module_name, sub_name):
    log_dir = './logs'
    ensure_dir(log_dir)
    log_file = '%s/desimartini_crawler_%s.log' % (log_dir, module_name.lower())
    file_size = 800 * 1024 * 1024
    rotate_handler = ConcurrentRotatingFileHandler(log_file, "a", file_size, backupCount=9, encoding="utf-8")
    date_fmt_str = '%Y-%m-%d %H:%M:%S'
    format_str = '[%(asctime)s][%(process)s][%(module)s:%(lineno)s %(funcName)s()][%(levelname)s] %(message)s'
    formatter = logging.Formatter(format_str, date_fmt_str)
    rotate_handler.setFormatter(formatter)
    logger = logging.getLogger(sub_name)
    if not logger.handlers:
        logger.addHandler(rotate_handler)
        logger.setLevel(logging.DEBUG)
    return logger

```
