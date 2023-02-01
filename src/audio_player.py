import threading
import sys
from audio_master import AudioMaster
import numpy as np
from log import error_handle

class AudioPlayer(threading.Thread):
    'thread for playing audio'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @error_handle
    def run(self):
        'play the audio track'
        while AudioMaster.is_running:

            # stop execution during pause
            while AudioMaster.is_paused or not AudioMaster.is_wav_loaded:
                pass

            #read audio frames and play them
            data = AudioMaster.wav.readframes(AudioMaster.BUFFER_SIZE)
            AudioMaster.stream.write(data)

            # Jump to START marker if file is over or the END marker has been reached
            if data == b'' or AudioMaster.get_current_frame() >= AudioMaster.LOOP_END:
                AudioMaster.set_current_frame(AudioMaster.LOOP_START)

        AudioMaster.close()

