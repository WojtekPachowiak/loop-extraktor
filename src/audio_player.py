import threading
import sys
from audio_settings import AudioSettings

class AudioPlayer(threading.Thread):
    'thread for playing audio'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)


    def run(self):
        'play the audio track'
        while AudioSettings.is_running:

            # stop execution during pause
            while AudioSettings.is_paused or not AudioSettings.is_wav_loaded:
                pass

            #read audio frames and play them
            data = AudioSettings.wav.readframes(AudioSettings.CHUNK_SIZE)
            AudioSettings.stream.write(data)

            # Jump to START marker if file is over or the END marker has been reached
            if data == b'' or AudioSettings.get_current_frame() >= AudioSettings.END:
                AudioSettings.set_current_frame(AudioSettings.START)

        AudioSettings.close()