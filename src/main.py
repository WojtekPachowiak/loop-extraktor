from audio_master import AudioMaster
from input import Input
from audio_player import AudioPlayer
from ui import UI
import typer
import threading
import time
import sys
from log import Logger, error_handle
import os


@error_handle
def main(
    output_dir: str = typer.Option(".", "--output_dir", "-o", help="Directory to save audio files to"),
    log:bool = typer.Option(False, "--log", "-l", help="Enable logging. Logs are saved to the CWD as 'log.txt'")
    ):
    
    Logger.initialize()
    Logger.LOG_TO_FILE = log

    AudioMaster.initialize(output_dir)
    input_thread= Input(name="Input",daemon = True)
    ui_thread = UI(name="UI", daemon = True)
    audio_thread = AudioPlayer(name="Audio_Player",daemon = True)
    threads  =[input_thread, ui_thread, audio_thread]

    start_threads(threads)
    while are_threads_alive(threads):
        time.sleep(0.5)
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.exit()


def start_threads(threads : list[threading.Thread]):
    [t.start() for t in threads]


def are_threads_alive(threads : list[threading.Thread]):
    return all([t.is_alive() for t in threads])


if __name__ == "__main__":
        typer.run(main)
    
