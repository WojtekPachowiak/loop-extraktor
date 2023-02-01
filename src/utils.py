# import logging
# from functools import wraps
# import sys

# LOGGING_ENABLED = True



# logging.basicConfig(filename="log.txt",
#                     filemode='w',
#                     format='%(threadName)s | %(levelname)s: %(message)s',
#                     level=logging.DEBUG)

# def log(msg :str):
#     if (LOGGING_ENABLED): logging.info(msg)

# def error(msg:str):
#     if (LOGGING_ENABLED): logging.error(msg)




# def error_handle(func):
#     @wraps(func)
#     def wrapper(*args, **kwargs):
#         try:
#             func(*args, **kwargs)
#         except Exception as e:
#             error(e)
#             sys.exit()
#     return wrapper