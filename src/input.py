from readchar import readkey, key
import threading
from audio_master import AudioMaster
import tkinter as tk
from tkinter import filedialog
from log import Logger, error_handle


class Input(threading.Thread):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        
        

    @error_handle
    def run(self):
        
        #initialize tkinter window for displaying file dialog
        root = tk.Tk()
        root.wm_attributes('-topmost', 1)
        root.withdraw()

        while AudioMaster.is_running:
            c = readkey()
            Logger.log(f"Input key: {c}")
            self._interpret(c)


    # SUSPENDED: the below function allows drag-n-dropping files into the console window, but it generates bugs.
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
                
    @error_handle
    def _interpret(self, k):
        'evaluate the keypress input'

        #input detected even if no audio file is loaded
        match k:
            case key.ESC:
                AudioMaster.is_running = False
            case 'q':
                AudioMaster.is_running = False
            case 'l':
                file_path = filedialog.askopenfilename()
                AudioMaster.load_audio(file_path)  

        if not AudioMaster.is_wav_loaded:
            return
        
        #input only detected if an audio file is loaded
        match k:
            case '[':
                AudioMaster.decrease_loop_length()
            case ']':
                AudioMaster.increase_loop_length()
            case key.RIGHT:
                AudioMaster.move_loop(1)
            case key.LEFT:
                AudioMaster.move_loop(-1)
            case 'p':
                AudioMaster.play() if AudioMaster.is_paused else AudioMaster.stop()
            case key.SPACE:
                AudioMaster.shuffle_loop_start()
            case 's':
                AudioMaster.save_loop_as_wav()
            case key.DOWN:
                AudioMaster.change_playback_speed(-0.3)
            case key.UP:
                AudioMaster.change_playback_speed(0.3)
                
            


        
