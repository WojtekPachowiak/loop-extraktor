import logging
from functools import wraps
import os
from time import sleep

class Logger:

    LOG_TO_FILE = False
    LAST_ERROR_MSG = None
    
    @classmethod
    def initialize(cls, level:int=logging.INFO):
        logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(threadName)s | %(levelname)s: %(message)s',
                    level=logging.DEBUG)
    
    @classmethod
    def log(cls, msg:str):
        if cls.LOG_TO_FILE: logging.info(msg)

    @classmethod
    def error(cls, msg:str):
        if cls.LOG_TO_FILE: logging.error(msg)
        cls.LAST_ERROR_MSG = msg


def error_handle(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            Logger.error(e)
    return wrapper