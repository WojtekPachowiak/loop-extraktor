from audio import Looper, KeyboardThread, PrintingThread
import sys
import time


def main(*args, **kwargs):
    path = "./morrigna.wav"

    #three threads
    looper = Looper(path, 13000, daemon=True)
    kthread = KeyboardThread(looper, daemon=True)
    pthread = PrintingThread(looper, daemon=True)

    threads = [looper,kthread,pthread]
    [t.start() for t in threads]

    #if any thread stops working, exit (all threads will kill themselves, because they are daemons)
    while all([t.is_alive() for t in threads]):
        time.sleep(0.5)

if __name__ == "__main__":
    main()