from dataclasses import dataclass
import os
from typing import Literal
import wave
import threading
import random
import pyaudio
from pathlib import Path
from datetime import datetime
from ui import UI
from input import Input
from audio import Audio
import sys
from utils import log
import time

class Looper():
    """
    Looper is the master of all - coordiantes the work of input, UI and audio threads. 
    Also stores information which is quieried by UI and audio threads.

    Terminology:
        "audio loop" - the audio range between START and END markers which is being looped over
        "audio track" - the full audio content of the loaded audio file
    """


    ############# INIT ###############

    def __init__(self, destpath:str="", **kwargs):
        """
        Args:
          srcpath (str) : path to the currently playing .wav file.
          destpath (str) : path to the directory where new .wav files are being saved 
          initial_loop_length (int): the length of the loop in samples after glitchy sound looper is activated. -1 that loop spans the whole audio track
        """
        super().__init__(**kwargs)
        self.CHUNK_SIZE = 1024
        self.is_running = True
        self.is_paused = False
        self.START = 0
        self.END = None
        self.MOVE_SPEED = 10000
        self.wav = None
        self.stream = None
        self.is_wav_loaded = False
        
        if not destpath.endswith("/") and not destpath.endswith("\\"):
            destpath += "/"
        self.destpath = destpath

        self.input_thread= Input(self, daemon = True)
        self.ui_thread = UI(self, daemon = True)
        self.audio_thread = Audio(self, daemon = True)
        self.input_thread.start()
        self.ui_thread.start()
        self.audio_thread.start()
                
        self.player = pyaudio.PyAudio()

        log("Init finished!")

        while self.is_running and self.input_thread.is_alive():
            time.sleep(0.5)

        

    ############# PLAY AUDIO ###############

    def play(self):
        "continue playback."
        log("Play!")
        self.is_paused = False

    def stop(self):
        "stop playback."
        log("Stop!")
        self.is_paused = True

    ########### CLOSE/TERMINATE APP ########

    def close(self):
        'clean up and terminate the app'
        log("Closing app!")
        self.audio_thread

        self.wav.close()
        self.stream.close()
        self.player.terminate()
        sys.exit()

    ############# CHANGE AUDIO FILE ###############

    def load_audio(self, path:str):
        'load audio file, start UI printing and immediately plays it'
        self.filepath = os.path.abspath(path)
        self.wav = wave.open(self.filepath, 'rb')
        self.stream = self.player.open(format=self.player.get_format_from_width(self.wav.getsampwidth()),
                                       channels=self.wav.getnchannels(),
                                       rate=self.wav.getframerate(),
                                       output=True)
        log("Audio loaded!")
        self.is_paused = False
        self.reset_loop()
        self.is_wav_loaded = True


    ############# QUEARY WAVE ###############

    def get_max_frames(self, ms_convert=False):
        'gets the number of frames the audio file contains'
        f = self.wav.getnframes()
        if ms_convert:
            f = self.frame_to_ms(f)
        return f

    def get_current_frame(self, ms_convert=False):
        'gets the frame number of the current frame'
        f = self.wav.tell()
        if ms_convert:
            f = self.frame_to_ms(f)
        return f
    
    

    def set_current_frame(self, frame: int):
        'sets the frame number of the current frame (the audio track starts being played from different point)'
        self.wav.setpos(frame)


    def frame_to_ms(self, frame:int):
        return round(frame/self.wav.getframerate(), 1)

    ############# AUDIO LOOP'S POSITION AND SIZE ###############

    def shuffle_loop_start(self):
        'randomly change the place of the audio loop (=move START and END markers unfiormly)'
        nf = random.randint(0, self.get_max_frames() - (self.END - self.START))
        diff = self.START - nf
        self.START = nf
        self.END = self.END - diff
        self.set_current_frame(nf)

    def decrease_loop_length(self):
        'shorten the audio loop'
        self.END -= self.MOVE_SPEED
        self.END = max(self.END, self.START)

    def increase_loop_length(self):
        'elongate the audio loop'
        self.END += self.MOVE_SPEED
        self.END = min(self.END, self.get_max_frames())

    def move_loop(self, direction: Literal[-1, 1]):
        'move the audio loop forward or backward. self.MOVE_SPEED controls the speed of movement'
        log("moving the loop")
        self.START += self.MOVE_SPEED * direction
        self.END += self.MOVE_SPEED * direction
        if self.START < 0:
            diff = 0 - self.START
            self.START += diff
            self.END += diff
            assert self.END <= self.get_max_frames()
        elif self.END > self.get_max_frames():
            diff = self.get_max_frames() - self.END
            self.START += diff
            self.END += diff
            assert self.START >= 0
    
    def reset_loop(self):
        'resets loop so that START==0 and END==maxframes. unpause'
        self.START = 0
        self.END = self.wav.getnframes()
    
    ############# SAVE AUDIO LOOP AS WAV ###############

    def save_loop_as_wav(self):
        'extract the audio located in the audio loop (between START and END markers) and save it as a new .wav file'
        #read frames from the current audio loop
        tmp = self.get_current_frame()
        self.set_current_frame(self.START)
        data = self.wav.readframes(self.END - self.START)
        self.set_current_frame(tmp)

        #save the new .wav file
        name = self.destpath + datetime.now().strftime("%H-%M-%S__%d-%m-%y") + ".wav"
        with wave.open(name, 'w') as f:
            f.setnchannels(self.wav.getnchannels())
            f.setsampwidth(self.wav.getsampwidth())
            f.setframerate(self.wav.getframerate())
            f.setnframes(int(len(data) / self.wav.getsampwidth()))
            f.writeframes(data)






