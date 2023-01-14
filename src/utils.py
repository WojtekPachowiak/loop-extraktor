import logging

logging.basicConfig(filename="log.txt",
                    filemode='w',
                    format='%(threadName)s | %(levelname)s: %(message)s',
                    level=logging.DEBUG)

def log(msg :str):
    logging.info(msg)

def error(msg:str):
    logging.error(msg)



