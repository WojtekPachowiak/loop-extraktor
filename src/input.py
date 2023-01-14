# getting keystroke input
from readchar import readkey, key
import threading
import sys
import msvcrt
from utils import log, error
from audio_settings import AudioSettings

class Input(threading.Thread):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def run(self):
        try:
            while AudioSettings.is_running:
                i, is_path = self._detect_console_input()  # waits to get input
                if is_path:
                    log(f"Provided path: {i}")
                    AudioSettings.load_audio(i)
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
            c = readkey()
            if msvcrt.kbhit():
                buf+=c
            #return drag-n-dropped filepath
            elif buf:
                buf+=c
                tmp = buf
                buf = ""
                return tmp, True
            #return single key input
            else:
                return c, False
                
            
    def _interpret(self, k):
        'evaluate the keypress input'
        if k == key.ESC:
                AudioSettings.is_running = False       
        if not AudioSettings.is_wav_loaded:
            return
            
        match k:
            case '[':
                AudioSettings.decrease_loop_length()
            case ']':
                AudioSettings.increase_loop_length()
            case key.RIGHT:
                AudioSettings.move_loop(1)
            case key.LEFT:
                AudioSettings.move_loop(-1)
            case 's':
                AudioSettings.play()
            case 'e':
                AudioSettings.stop()
            case key.SPACE:
                AudioSettings.shuffle_loop_start()
            case 'r':
                AudioSettings.save_loop_as_wav()
        
