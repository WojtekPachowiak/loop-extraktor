from audio_master import AudioMaster
from input import Input
from audio_player import AudioPlayer
from ui import UI
import typer
import threading
import time
import sys

def main():

    AudioMaster.initialize("saved_audio")
    input_thread= Input(name="Input",daemon = True)
    ui_thread = UI(name="UI", daemon = True)
    audio_thread = AudioPlayer(name="Audio_Player",daemon = True)
    threads  =[input_thread, ui_thread, audio_thread]

    start_threads(threads)
    while are_threads_alive(threads):
        time.sleep(0.5)
    sys.exit()


def start_threads(threads : list[threading.Thread]):
    [t.start() for t in threads]

def are_threads_alive(threads : list[threading.Thread]):
    return all([t.is_alive() for t in threads])


if __name__ == "__main__":
        typer.run(main)
    
