from consoledraw import Console
import threading
from audio import Looper
import time

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
║   'SPACE' to randomly switch position
║   'S' to unpause the recording
║   'E' to pause the recording
║   ']' to increase loop length
║   '[' to decrease loop length
║   'RIGHT_ARROW' to move loop to the right
║   'LEFT_ARROW' to move loop to the left
    'R' to save the selected loop as .wav
╚════════════════════════════════
                """

                self.console.print(format)
            time.sleep(self.refresh_interval)
