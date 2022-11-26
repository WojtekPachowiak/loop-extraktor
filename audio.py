import os
from typing import Literal, Optional
import wave
import threading
import sys
import random
import time
# PyAudio Library
import pyaudio

# getting keystroke input
from readchar import readkey, key

# controlling what gets printed in the console
from consoledraw import Console

# class KillableThread(threading.Thread):
#   __ALIVE__ = True

#   def __init__(self):
#     super().__init__()

#   def kill(self):
#     'Kill this process'
#     self.__ALIVE__ = False


class Looper(threading.Thread):
    """
    TODO
    """

    CHUNK = 1024
    RUNNING = True
    PAUSE = False
    START = 0
    END = None
    MOVE_SPEED = 10000

    def __init__(self, filepath, starting_loop_length: int = -1, **kwargs):
        """
        Initialize `Looper` class.

        ARGS:
          filepath (String) : File Path to .wav file.

        """
        super().__init__(**kwargs)
        self.filepath = os.path.abspath(filepath)
        # Open Wave File and start play!
        self.wf = wave.open(self.filepath, 'rb')
        self.player = pyaudio.PyAudio()
        # Open Output Stream (basen on PyAudio tutorial)
        self.stream = self.player.open(format=self.player.get_format_from_width(self.wf.getsampwidth()),
                                       channels=self.wf.getnchannels(),
                                       rate=self.wf.getframerate(),
                                       output=True)

        self.END = self.get_max_frames() if starting_loop_length == - \
            1 else starting_loop_length
        assert self.END != None

    def run(self):
        while self.RUNNING:
            # pause
            while self.PAUSE:
                pass
            data = self.wf.readframes(self.CHUNK)
            self.stream.write(data)

            # Jump to START marker if file is over or the END marker has been reached
            if data == b'' or self.get_current_frame() >= self.END:
                self.set_current_frame(self.START)
                # self.wf.rewind()

        self.stream.close()
        self.player.terminate()

    def play(self):
        "Continue playback."
        self.PAUSE = False

    def stop(self):
        "Stop playback."
        self.PAUSE = True

    def get_max_frames(self):
        return self.wf.getnframes()

    def get_current_frame(self):
        return self.wf.tell()

    def set_current_frame(self, frame: int):
        self.wf.setpos(frame)

    def shuffle_loop_start(self):
        'randomly change the place of the loop (=move start and end markers unfiormly)'
        nf = random.randint(0, self.get_max_frames() - (self.END - self.START))
        diff = self.START - nf
        self.START = nf
        self.END = self.END - diff

        self.set_current_frame(nf)

    def decrease_loop_length(self):
        self.END -= self.MOVE_SPEED
        self.END = max(self.END, self.START)

    def increase_loop_length(self):
        self.END += self.MOVE_SPEED
        self.END = min(self.END, self.get_max_frames())

    def move_loop(self, direction: Literal[-1, 1]):
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


class KeyboardThread(threading.Thread):

    def __init__(self, looper, **kwargs):
        super(KeyboardThread, self).__init__(**kwargs)
        self.looper = looper

    def run(self):
        while True:
            k = readkey()  # waits to get input
            self._interpret(k)

    def _interpret(self, k):
        # evaluate the keyboard input
        match k:
            case '[':
                self.looper.decrease_loop_length()
            case ']':
                self.looper.increase_loop_length()
            case key.RIGHT:
                self.looper.move_loop(1)
            case key.LEFT:
                self.looper.move_loop(-1)
            case 's':
                self.looper.play()
            case 'e':
                self.looper.stop()
            case key.SPACE:
                self.looper.shuffle_loop_start()
            case key.ESC:
                sys.exit()


class PrintingThread(threading.Thread):
    'Thread responsible for displaying in the console things such as frame count, controls instructions or current settings'
    timeline_len = 80
    timeline_char = '█'
    refresh_interval = 0.05  # in seconds

    def __init__(self, looper: Looper, **kwargs):
        super(PrintingThread, self).__init__(**kwargs)
        self.looper = looper
        self.console = Console()

    def run(self):
        while True:
            with self.console:
                max = self.looper.get_max_frames()
                curr = self.looper.get_current_frame()
                start = self.looper.START
                end = self.looper.END
                ralign = len(str(max))
                marker = '^'
                timeline = self.timeline_char * \
                    int(curr/max * self.timeline_len)
                start_marker_pos = int(start/max * self.timeline_len)
                end_marker_pos = int(end/max * self.timeline_len)
                if start_marker_pos != end_marker_pos:
                    markers = " " * (start_marker_pos) + "^" + " " * (
                        end_marker_pos - start_marker_pos-1) + "^" + " "*(ralign-end_marker_pos)
                else:
                    markers = " " * (start_marker_pos) + "^" + \
                        " " * (ralign-start_marker_pos)
                format = f"""
╔══════ Frames ══════════════════
║  Total:   {max:>{ralign}}
║  Current: {curr:>{ralign}}
║  [{timeline:<{self.timeline_len}}]
║   {markers}
╚══════ Loop ════════════════════
║   Start:  {start:>{ralign}}
║   End:    {end:>{ralign}}
║   Length: {end-start:>{ralign}}
╚══════ Controls ════════════════
║   'SPACE' to switch position
║   'S' to unpause the recording
║   'E' to pause the recording
║   ']' to increase loop length
║   '[' to decrease loop length
║   'RIGHT_ARROW' to move loop to the right
║   'LEFT_ARROW' to move loop to the left
╚════════════════════════════════
                """

                self.console.print(format)
            time.sleep(self.refresh_interval)
