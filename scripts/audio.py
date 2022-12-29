from dataclasses import dataclass
import os
from typing import Literal
import wave
import threading
import random
import pyaudio
from pathlib import Path
from datetime import datetime
    

class Looper(threading.Thread):
    """
    Terminology:
        "audio loop" - the audio range between START and END markers which is being looped over
        "audio track" - the full audio content of the loaded audio file
    """

    CHUNK_SIZE = 1024
    RUNNING = True
    PAUSE = False
    START = 0
    END = None
    MOVE_SPEED = 10000
    
    @dataclass
    class WaveMetadata:
        nchannels:int
        sampwidth:int
        framerate:int
        nframes:int

    ############# INIT ###############

    def __init__(self, srcpath:Path, destpath:Path, initial_loop_length: int = -1, **kwargs):
        """
        Args:
          srcpath (str) : path to the currently playing .wav file.
          destpath (str) : path to the directory where new .wav files are being saved 
          initial_loop_length (int): the length of the loop in samples after glitchy sound looper is activated. -1 that loop spans the whole audio track
        """
        super().__init__(**kwargs)

        self.filepath = os.path.abspath(srcpath)

        self.wav = wave.open(self.filepath, 'rb')
        self.wav_metadata = Looper.WaveMetadata(
            nchannels=self.wav.getnchannels(), 
            sampwidth=self.wav.getsampwidth(), 
            framerate=self.wav.getframerate(),
            nframes = self.wav.getnframes()
            )

        self.player = pyaudio.PyAudio()
        self.stream = self.player.open(format=self.player.get_format_from_width(self.wav_metadata.sampwidth),
                                       channels=self.wav_metadata.nchannels,
                                       rate=self.wav_metadata.framerate,
                                       output=True)

        self.END = self.wav_metadata.nframes if initial_loop_length == -1 else initial_loop_length
        assert self.END != None

    ############# PLAY AUDIO ###############

    def run(self):
        'play the audio track'
        while self.RUNNING:

            # stop execution during pause
            while self.PAUSE:
                pass

            #read audio frames and play them
            data = self.wav.readframes(self.CHUNK_SIZE)
            self.stream.write(data)

            # Jump to START marker if file is over or the END marker has been reached
            if data == b'' or self.get_current_frame() >= self.END:
                self.set_current_frame(self.START)

        #clean up
        self.wav.close()
        self.stream.close()
        self.player.terminate()

    def play(self):
        "continue playback."
        self.PAUSE = False

    def stop(self):
        "stop playback."
        self.PAUSE = True

    ############# QUEARY WAVE ###############

    def get_max_frames(self):
        'gets the number of frames the audio file contains'
        return self.wav.getnframes()

    def get_current_frame(self):
        'gets the frame number of the current frame'
        return self.wav.tell()

    def set_current_frame(self, frame: int):
        'sets the frame number of the current frame (the audio track starts being played from different point)'
        self.wav.setpos(frame)

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
    
    ############# SAVE AUDIO LOOP AS WAV ###############

    def save_loop_as_wav(self):
        'extract the audio located in the audio loop (between START and END markers) and save it as a new .wav file'
        #read frames from the current audio loop
        tmp = self.get_current_frame()
        self.set_current_frame(self.START)
        data = self.wav.readframes(self.END - self.START)
        self.set_current_frame(tmp)

        #save the new .wav file
        name = datetime.now().strftime("%H-%M-%S__%d-%m-%y") + ".wav"
        with wave.open(name, 'w') as f:
            f.setnchannels(self.wav_metadata.nchannels)
            f.setsampwidth(self.wav_metadata.sampwidth)
            f.setframerate(self.wav_metadata.framerate)
            f.setnframes(int(len(data) / self.wav_metadata.sampwidth))
            f.writeframes(data)






