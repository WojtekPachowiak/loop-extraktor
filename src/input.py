# getting keystroke input
from readchar import readkey, key
import threading
import sys
import msvcrt


class KeyboardThread(threading.Thread):

    def __init__(self, looper, **kwargs):
        super(KeyboardThread, self).__init__(**kwargs)
        self.looper = looper

    def run(self):
        while True:
            k = self._detect_console_input()  # waits to get input
            self._interpret(k)


    def _detect_console_input(self):
        'detects single key input as well as drag-n-dropped filepaths'
        buf = ""
        while True:
            c = msvcrt.getwch()

            if msvcrt.kbhit():
                buf+=c
            #return drag-n-dropped filepath
            elif buf:
                buf+=c
                return buf
            #return single key input
            else:
                return c
                
            

    def _interpret(self, k):
        # evaluate the keyboard input
        match k:
            case '[':
                self.looper.decrease_loop_length()
            case ']':
                self.looper.increase_loop_length()
            case key.RIGHT:
                self.looper.move_loop(1)
            case key.LEFT:
                self.looper.move_loop(-1)
            case 's':
                self.looper.play()
            case 'e':
                self.looper.stop()
            case key.SPACE:
                self.looper.shuffle_loop_start()
            case 'r':
                self.looper.save_loop_as_wav()
            case key.ESC:
                sys.exit()