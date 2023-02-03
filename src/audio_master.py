from dataclasses import dataclass
import os
from typing import Literal
import wave
import random
import pyaudio
from datetime import datetime
import sys
from pathlib import Path
from log import Logger, error_handle
# from pedalboard import 
from pedalboard.io import AudioFile

SAMPWIDTH = pyaudio.paFloat32

class AudioMaster():
    """
    Stores information which is quiried by UI and audio threads. 
    Contains functions which manipulate the audio player (for example, setting playback position/speed or loop position/size).

    Terminology:
        "audio loop" - the audio range between START and END markers which is being looped over
        "audio track" - the full audio content of the loaded audio file
    """


    ############# INIT ###############
    
    @classmethod
    def initialize(cls, destpath:str="", **kwargs):
        """
        Args:
          destpath (str) : path to the directory where new .wav files are being saved 
        """

        cls.BUFFER_SIZE = 1024 # how many frames to read at once
        cls.LOOP_START = 0 # frame number of the start of the audio loop
        cls.LOOP_END = None # frame number of the end of the audio loop
        cls.SEEK_SPEED = 10000 # how many frames to jump when seeking
        cls.PLAYBACK_SPEED = 1.0 # playback speed of the audio file
        cls.PLAYBACK_SPEED_MAX = 2.0 # maximum playback speed
        cls.PLAYBACK_SPEED_MIN = 0.1 # minimum playback speed

        cls.is_running = True # is the app running?
        cls.is_paused = False 
        cls.is_audio_loaded = False # is an audio file loaded?

        cls.audio = None 
        cls.stream = None
        cls.filepath = None
        cls.destpath = os.path.abspath(destpath)
        cls.player = pyaudio.PyAudio()

        Logger.log("Init finished!")

        

    ############# PLAY AUDIO ###############
    
    @classmethod
    def play(cls):
        "continue playback."
        Logger.log("Play!")
        cls.is_paused = False
    
    @classmethod
    def stop(cls):
        "stop playback."
        Logger.log("Stop!")
        cls.is_paused = True

    ########### CLOSE/TERMINATE APP ########
    
    @classmethod
    def close(cls):
        'clean up and terminate the app'
        Logger.log("Closing app!")

        cls.audio.close()
        cls.stream.close()
        cls.player.terminate()
        sys.exit()

    ############# CHANGE AUDIO FILE ###############
    
    @classmethod
    def load_audio(cls, path:str):
        'load audio file, start UI printing and immediately play it'

        cls.filepath = os.path.abspath(path)
        cls.audio = AudioFile(cls.filepath)
        cls.stream = cls.player.open(format=SAMPWIDTH,
                                       channels=cls.audio.num_channels,
                                       rate=int(cls.audio.samplerate),
                                       output=True)
        Logger.log("Audio loaded!")
        cls.is_paused = False
        cls.reset_loop()
        cls.is_audio_loaded = True
        

    ############# QUEARY AND MODIFY WAVE ###############
    
    @classmethod
    def get_max_frames(cls, ms_convert=False):
        '''
        gets the number of frames the audio file contains
        
        Args:
            ms_convert (bool) : if True, returns the number of frames in milliseconds
        '''
        f = cls.audio.frames
        if ms_convert:
            f = cls.frame_to_ms(f)
        return f


    @classmethod
    def get_current_frame(cls, ms_convert=False):
        '''
        gets the frame number of the current frame
        
        Args:
            ms_convert (bool) : if True, returns the current frame in milliseconds
        '''
        f = cls.audio.tell()
        if ms_convert:
            f = cls.frame_to_ms(f)
        return f
    

    @classmethod
    def change_playback_speed(cls, delta:float):
        '''
        sets the framerate of the audio file
        
        Args:
            change (float) : how much to change the playback speed (1.0 = normal speed) 
        '''
        cls.PLAYBACK_SPEED += delta
        cls.PLAYBACK_SPEED = max(cls.PLAYBACK_SPEED, cls.PLAYBACK_SPEED_MIN)
        cls.PLAYBACK_SPEED = min(cls.PLAYBACK_SPEED, cls.PLAYBACK_SPEED_MAX)
        cls.stream = cls.player.open(format=SAMPWIDTH,
                                       channels=cls.audio.num_channels,
                                       rate=int(cls.audio.samplerate * cls.PLAYBACK_SPEED),
                                       output=True)

    
    @classmethod
    def set_current_frame(cls, frame: int):
        'sets the frame number of the current frame (the audio track starts being played from different point)'
        cls.audio.seek(frame)

    
    @classmethod
    def frame_to_ms(cls, frame:int):
        return round(frame/cls.audio.samplerate, 1)

    ############# AUDIO LOOP'S POSITION AND SIZE ###############
    
    @classmethod
    def shuffle_loop_start(cls):
        'randomly change the place of the audio loop (=move START and END markers unfiormly)'
        nf = random.randint(0, cls.get_max_frames() - (cls.LOOP_END - cls.LOOP_START))
        diff = cls.LOOP_START - nf
        cls.LOOP_START = nf
        cls.LOOP_END = cls.LOOP_END - diff
        cls.set_current_frame(nf)
    
    @classmethod
    def decrease_loop_length(cls):
        'shorten the audio loop'
        cls.LOOP_END -= cls.SEEK_SPEED
        cls.LOOP_END = max(cls.LOOP_END, cls.LOOP_START)
    
    @classmethod
    def increase_loop_length(cls):
        'elongate the audio loop'
        cls.LOOP_END += cls.SEEK_SPEED
        cls.LOOP_END = min(cls.LOOP_END, cls.get_max_frames())
    
    @classmethod
    def move_loop(cls, direction: Literal[-1, 1]):
        'move the audio loop forward or backward. cls.MOVE_SPEED controls the speed of movement'
        Logger.log("moving the loop")
        s = cls.LOOP_START + cls.SEEK_SPEED * direction
        e = cls.LOOP_END + cls.SEEK_SPEED * direction
        if s < 0:
            diff = 0 - s
            s += diff
            e += diff
            assert e <= cls.get_max_frames()
        elif e > cls.get_max_frames():
            diff = cls.get_max_frames() - e
            s += diff
            e += diff
            assert s >= 0
        cls.LOOP_START = s
        cls.LOOP_END = e
        cls.set_current_frame(cls.LOOP_START)

    
    @classmethod
    def reset_loop(cls):
        'resets loop so that START==0 and END==maxframes. unpause'
        cls.LOOP_START = 0
        cls.LOOP_END = cls.audio.frames
    
    ############# SAVE AUDIO LOOP AS WAV ###############
    
    @classmethod
    def save_loop_as_wav(cls):
        'extract the audio located in the audio loop (between START and END markers) and save it as a new .wav file'
        #read frames from the current audio loop
        tmp = cls.get_current_frame()
        cls.set_current_frame(cls.LOOP_START)
        data = cls.audio.read(cls.LOOP_END - cls.LOOP_START)
        cls.set_current_frame(tmp)

        #save the new .wav file
        path = os.path.join(cls.destpath, datetime.now().strftime("%H-%M-%S__%d-%m-%y") + ".wav")
        with wave.open(path, 'w') as f:
            f.setnchannels(cls.audio.num_channels)
            f.setsampwidth(SAMPWIDTH)
            f.setframerate(cls.audio.samplerate)
            f.setnframes(int(len(data) / SAMPWIDTH))
            f.writeframes(data) 


    ########### AUDIO EFFECTS  ################
    # SUSPENDED FOR NOW
    # @classmethod
    # def apply_effects(cls, data : bytes) -> bytes:
    #     data = np.fromstring(data,dtype=np.int16)
    #     max_16_bit_sample_value = (2 ** 15)
    #     data = data.astype(np.float32) / max_16_bit_sample_value
    #     board = Pedalboard([Chorus(), Reverb(room_size=0.25)])
    #     data = board(data, cls.wav.getframerate(), reset=False)
    #     data = data.tobytes()
    #     return data


    ########################

    @classmethod
    def get_output_latency(cls):
        return cls.stream.get_output_latency()
        







