import threading
import sys

class Audio(threading.Thread):
    'thread for playing audio'
    
    def __init__(self, looper, **kwargs):
        super().__init__(**kwargs)
        self.looper = looper


    def run(self):
        'play the audio track'
        while self.looper.is_running:

            # stop execution during pause
            while self.looper.is_paused or not self.looper.is_wav_loaded:
                pass

            #read audio frames and play them
            data = self.looper.wav.readframes(self.looper.CHUNK_SIZE)
            self.looper.stream.write(data)

            # Jump to START marker if file is over or the END marker has been reached
            if data == b'' or self.looper.get_current_frame() >= self.looper.END:
                self.looper.set_current_frame(self.looper.START)

        self.looper.close()