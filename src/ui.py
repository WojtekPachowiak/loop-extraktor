import threading
from audio import Looper
import time


from rich.progress import Progress
from rich.progress_bar import ProgressBar

from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn, MofNCompleteColumn, Task
from rich.table import Column
from rich.panel import Panel
from rich.text import Text


from rich.console import Group
from rich.console import Console
from rich.table import Table
from rich import box
import yaml

from rich.layout import Layout
from rich.live import Live


class PrintingThread(threading.Thread):
    'Thread responsible for displaying in the console things such as frame count, controls instructions or current settings'

    def __init__(self, looper: Looper, **kwargs):
        super().__init__(**kwargs)
        self.looper = looper
        self.console = Console()
        self.setup_ui()

    
    def run(self):
        with Live(self.layout, refresh_per_second=10, screen=True):
            while True:
                time.sleep(0.1)
                self.audio_bar.update(self.audio_playing_task, completed=self.looper.get_current_frame())


    def setup_ui(self):
        'sets up all the TUI components that will be displayed in Live loop'
        # text_column2 = MofNCompleteColumn ()
        self.audio_bar = Progress(AudioProgressColumn(looper=self.looper))
        self.audio_playing_task = self.audio_bar.add_task("...", total=self.looper.get_max_frames(),console_width=self.audio_bar.console.width)

        #setup table with info about the playback
        #TODO
        
        #setup table with info about controls
        with open('controls.yaml', 'r') as file:
            controls = yaml.safe_load(file)
        controls_table = Table(show_edge=True,title_justify="left" ,show_header=False, box= box.ROUNDED, expand=True)
        controls_table.add_column("Key", justify="right", style="dim cyan")
        controls_table.add_column("explanation", justify="left")
        for k,v in controls.items():
            controls_table.add_row(k, v)

        #setup table with info about the loop
        loop_table = Table(show_edge=True,title_justify="left" ,show_header=False, box= box.ROUNDED, expand=True)
        loop_table.add_column("Property",justify="right", style="dim cyan")
        loop_table.add_column("Frame")
        loop_table.add_row("Start",str(102))
        loop_table.add_row("End",str(1214))
        loop_table.add_row("Length",str(1214-102))

        #gather all the above defined elements into a common layout
        self.layout = Layout(name="root")
        self.layout.split(
            Layout(name="timeline",size=3),
            Layout(name="rest"),
        )
        self.layout["rest"].split_row(
            Layout(name="info"),
            Layout(name="controls")
        )
        self.layout["timeline"].update(Panel(self.audio_bar))
        self.layout["info"].update(loop_table)
        self.layout["controls"].update(controls_table)




class AudioProgressColumn(TextColumn):
    'custom progress bar column for displaying audio progress and a loop'
    def __init__(self, looper:Looper, text_format="", *args, **kwargs) -> None:
        self.looper = looper
        super().__init__(text_format, *args, **kwargs)

    def render(self, task: Task) -> Text:
        width = task.fields["console_width"] - 6
        # ls = task.fields["loop_start"]
        ls = self.looper.START
        # le = task.fields["loop_end"]
        le = self.looper.END
        empty = "═"
        full = "|" 
        right_end = "╞"
        left_end = "╡"
        
        s = int(ls/task.total * width)
        e = int(le/task.total * width)+1
        
        _text = (
            right_end + 
            empty * int(task.percentage/100 * width) + 
            full + 
            empty * int( (1.-task.percentage/100) * width) +
            left_end
        )
        # _text =   _text[:s] + "[cyan]" + _text[s:e] + "[/cyan]" + _text[e:]
        text = Text(_text, justify=self.justify)
        text.stylize("bold red", s, e)

        return text











#         while True:
            
#             with self.console:
#                 max = self.looper.get_max_frames()
#                 curr = self.looper.get_current_frame()
#                 start = self.looper.START
#                 end = self.looper.END
#                 ralign = len(str(max))
#                 marker = '^'
#                 timeline = self.timeline_char * \
#                     int(curr/max * self.timeline_len)
#                 start_marker_pos = int(start/max * self.timeline_len)
#                 end_marker_pos = int(end/max * self.timeline_len)
#                 if start_marker_pos != end_marker_pos:
#                     markers = " " * (start_marker_pos) + "^" + " " * (
#                         end_marker_pos - start_marker_pos-1) + "^" + " "*(ralign-end_marker_pos)
#                 else:
#                     markers = " " * (start_marker_pos) + "^" + \
#                         " " * (ralign-start_marker_pos)
#                 format = f"""
# ╔══════ Frames ══════════════════
# ║  Total:   {max:>{ralign}}
# ║  Current: {curr:>{ralign}}
# ║  [{timeline:<{self.timeline_len}}]
# ║   {markers}
# ╚══════ Loop ════════════════════
# ║   Start:  {start:>{ralign}}
# ║   End:    {end:>{ralign}}
# ║   Length: {end-start:>{ralign}}
# ╚══════ Controls ════════════════
# ║   'SPACE' to randomly switch position
# ║   'S' to unpause the recording
# ║   'E' to pause the recording
# ║   ']' to increase loop length
# ║   '[' to decrease loop length
# ║   'RIGHT_ARROW' to move loop to the right
# ║   'LEFT_ARROW' to move loop to the left
#     'R' to save the selected loop as .wav
# ╚════════════════════════════════
#                 """

#                 self.console.print(format)
#             time.sleep(self.refresh_interval)
