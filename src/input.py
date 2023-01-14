# getting keystroke input
from readchar import readkey, key
import threading
import sys
import msvcrt
from utils import log, error

class Input(threading.Thread):

    def __init__(self, looper, **kwargs):
        super().__init__(**kwargs)
        self.looper = looper

    def run(self):
        try:
            while self.looper.is_running:
                i, is_path = self._detect_console_input()  # waits to get input
                if is_path:
                    log(f"Provided path: {i}")
                    self.looper.load_audio(i)
                else:
                    log(f"Provided key: {i}")
                    self._interpret(i)
        except Exception as e:
            error(e)
            sys.exit()


    def _detect_console_input(self):
        "detects single key input as well as drag-n-dropped filepaths. Additionally returns True if it's a path and False otherwise"
        buf = ""
        while True:
            c = msvcrt.getwch()
            if msvcrt.kbhit():
                buf+=c
            #return drag-n-dropped filepath
            elif buf:
                buf+=c
                return buf, True
            #return single key input
            else:
                return c, False
                
            
    def _interpret(self, k):
        'evaluate the keypress input'
        if k == key.ESC:
                self.looper.is_running = False       
        if not self.looper.is_wav_loaded:
            return
            
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
        
