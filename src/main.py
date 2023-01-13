from audio import Looper
from ui import PrintingThread
from input import KeyboardThread
import time
import typer
import sys


def main(starting_loop_length: int=-1):

    #three threads
    looper = Looper(daemon=True)
    kthread = KeyboardThread(looper, daemon=True)
    pthread = PrintingThread(looper, daemon=True)
    threads = [looper,kthread,pthread]

    #run all the threads
    [t.start() for t in threads]

    #if any thread stops working, exit (all threads will kill themselves, because they are daemons)
    while all([t.is_alive() for t in threads]):
        time.sleep(0.5)
        
    sys.exit()


if __name__ == "__main__":
    typer.run(main)