# getting keystroke input
from readchar import readkey, key
import threading
import sys
from utils import log, error_handle
from audio_master import AudioMaster

class Input(threading.Thread):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @error_handle
    def run(self):
        while AudioMaster.is_running:
            c = readkey()
            log(f"Input key: {c}")
            self._interpret(c)



    # def _detect_console_input(self):
    #     "detects single key input as well as drag-n-dropped filepaths. Additionally returns True if it's a path and False otherwise"
    #     buf = ""
    #     while True:
    #         c = readkey()
    #         if msvcrt.kbhit():
    #             buf+=c
    #         #return drag-n-dropped filepath
    #         elif buf:
    #             buf+=c
    #             tmp = buf
    #             buf = ""
    #             return tmp, True
    #         #return single key input
    #         else:
    #             return c, False
                
            
    def _interpret(self, k):
        'evaluate the keypress input'
        match k:
            case key.ESC:
                AudioMaster.is_running = False
            case 'l':
                import tkinter as tk
                from tkinter import filedialog
                root = tk.Tk()
                root.wm_attributes('-topmost', 1)
                root.withdraw()

                file_path = filedialog.askopenfilename()
                AudioMaster.load_audio(file_path)  

        if not AudioMaster.is_wav_loaded:
            return
            
        match k:
            case '[':
                AudioMaster.decrease_loop_length()
            case ']':
                AudioMaster.increase_loop_length()
            case key.RIGHT:
                AudioMaster.move_loop(1)
            case key.LEFT:
                AudioMaster.move_loop(-1)
            case key.SPACE:
                AudioMaster.play() if AudioMaster.is_paused else AudioMaster.stop()
            case 's':
                AudioMaster.shuffle_loop_start()
            case 'r':
                AudioMaster.save_loop_as_wav()
            


        
