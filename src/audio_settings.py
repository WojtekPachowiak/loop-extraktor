from dataclasses import dataclass
import os
from typing import Literal
import wave
import random
import pyaudio
from pathlib import Path
from datetime import datetime
import sys
from utils import log
import time

class AudioSettings():
    """
    Looper is the master of all - coordiantes the work of input, UI and audio threads. 
    Also stores information which is quieried by UI and audio threads.

    Terminology:
        "audio loop" - the audio range between START and END markers which is being looped over
        "audio track" - the full audio content of the loaded audio file
    """


    ############# INIT ###############
    
    @classmethod
    def initialize(cls, destpath:str="", **kwargs):
        """
        Args:
          srcpath (str) : path to the currently playing .wav file.
          destpath (str) : path to the directory where new .wav files are being saved 
          initial_loop_length (int): the length of the loop in samples after glitchy sound looper is activated. -1 that loop spans the whole audio track
        """
        cls.CHUNK_SIZE = 1024
        cls.is_running = True
        cls.is_paused = False
        cls.START = 0
        cls.END = None
        cls.MOVE_SPEED = 10000
        cls.wav = None
        cls.stream = None
        cls.is_wav_loaded = False
        
        if not destpath.endswith("/") and not destpath.endswith("\\"):
            destpath += "/"
        cls.destpath = destpath
                
        cls.player = pyaudio.PyAudio()

        log("Init finished!")

        

    ############# PLAY AUDIO ###############
    
    @classmethod
    def play(cls):
        "continue playback."
        log("Play!")
        cls.is_paused = False
    
    @classmethod
    def stop(cls):
        "stop playback."
        log("Stop!")
        cls.is_paused = True

    ########### CLOSE/TERMINATE APP ########
    
    @classmethod
    def close(cls):
        'clean up and terminate the app'
        log("Closing app!")
        cls.audio_thread

        cls.wav.close()
        cls.stream.close()
        cls.player.terminate()
        sys.exit()

    ############# CHANGE AUDIO FILE ###############
    
    @classmethod
    def load_audio(cls, path:str):
        'load audio file, start UI printing and immediately plays it'
        cls.filepath = os.path.abspath(path)
        cls.wav = wave.open(cls.filepath, 'rb')
        cls.stream = cls.player.open(format=cls.player.get_format_from_width(cls.wav.getsampwidth()),
                                       channels=cls.wav.getnchannels(),
                                       rate=cls.wav.getframerate(),
                                       output=True)
        log("Audio loaded!")
        cls.is_paused = False
        cls.reset_loop()
        cls.is_wav_loaded = True


    ############# QUEARY WAVE ###############
    
    @classmethod
    def get_max_frames(cls, ms_convert=False):
        'gets the number of frames the audio file contains'
        f = cls.wav.getnframes()
        if ms_convert:
            f = cls.frame_to_ms(f)
        return f
    
    @classmethod
    def get_current_frame(cls, ms_convert=False):
        'gets the frame number of the current frame'
        f = cls.wav.tell()
        if ms_convert:
            f = cls.frame_to_ms(f)
        return f
    
    
    
    @classmethod
    def set_current_frame(cls, frame: int):
        'sets the frame number of the current frame (the audio track starts being played from different point)'
        cls.wav.setpos(frame)

    
    @classmethod
    def frame_to_ms(cls, frame:int):
        return round(frame/cls.wav.getframerate(), 1)

    ############# AUDIO LOOP'S POSITION AND SIZE ###############
    
    @classmethod
    def shuffle_loop_start(cls):
        'randomly change the place of the audio loop (=move START and END markers unfiormly)'
        nf = random.randint(0, cls.get_max_frames() - (cls.END - cls.START))
        diff = cls.START - nf
        cls.START = nf
        cls.END = cls.END - diff
        cls.set_current_frame(nf)
    
    @classmethod
    def decrease_loop_length(cls):
        'shorten the audio loop'
        cls.END -= cls.MOVE_SPEED
        cls.END = max(cls.END, cls.START)
    
    @classmethod
    def increase_loop_length(cls):
        'elongate the audio loop'
        cls.END += cls.MOVE_SPEED
        cls.END = min(cls.END, cls.get_max_frames())
    
    @classmethod
    def move_loop(cls, direction: Literal[-1, 1]):
        'move the audio loop forward or backward. cls.MOVE_SPEED controls the speed of movement'
        log("moving the loop")
        cls.START += cls.MOVE_SPEED * direction
        cls.END += cls.MOVE_SPEED * direction
        if cls.START < 0:
            diff = 0 - cls.START
            cls.START += diff
            cls.END += diff
            assert cls.END <= cls.get_max_frames()
        elif cls.END > cls.get_max_frames():
            diff = cls.get_max_frames() - cls.END
            cls.START += diff
            cls.END += diff
            assert cls.START >= 0
    
    @classmethod
    def reset_loop(cls):
        'resets loop so that START==0 and END==maxframes. unpause'
        cls.START = 0
        cls.END = cls.wav.getnframes()
    
    ############# SAVE AUDIO LOOP AS WAV ###############
    
    @classmethod
    def save_loop_as_wav(cls):
        'extract the audio located in the audio loop (between START and END markers) and save it as a new .wav file'
        #read frames from the current audio loop
        tmp = cls.get_current_frame()
        cls.set_current_frame(cls.START)
        data = cls.wav.readframes(cls.END - cls.START)
        cls.set_current_frame(tmp)

        #save the new .wav file
        name = cls.destpath + datetime.now().strftime("%H-%M-%S__%d-%m-%y") + ".wav"
        with wave.open(name, 'w') as f:
            f.setnchannels(cls.wav.getnchannels())
            f.setsampwidth(cls.wav.getsampwidth())
            f.setframerate(cls.wav.getframerate())
            f.setnframes(int(len(data) / cls.wav.getsampwidth()))
            f.writeframes(data)






