import logging
from functools import wraps
import sys

logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(threadName)s | %(levelname)s: %(message)s',
                    level=logging.DEBUG)

def log(msg :str):
    logging.info(msg)

def error(msg:str):
    logging.error(msg)



def error_handle(func):
    @wraps(func)
    def warapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            error(e)
            sys.exit()
    return warapper