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












class MyProgress(Progress):
    def get_renderables(self):
        title=""
        # if len(self.tasks) >0:
        #     title = f"{self.tasks[0].completed}/{self.tasks[0].total}"
        yield Panel(self.make_tasks_table(self.tasks), title=title,title_align="left")

class AudioProgressColumn(TextColumn):
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


class PrintingThread(threading.Thread):
    'Thread responsible for displaying in the console things such as frame count, controls instructions or current settings'
    timeline_len = 80
    timeline_char = '━'
    refresh_interval = 0.05  # in seconds

    def __init__(self, looper: Looper, **kwargs):
        super(PrintingThread, self).__init__(**kwargs)
        self.looper = looper
        self.console = Console()


    def run(self):
        audio_progress_column = AudioProgressColumn(looper=self.looper)
        # text_column2 = MofNCompleteColumn ()
        progress = MyProgress(audio_progress_column)
        task1 = progress.add_task("[red]Playing...", total=self.looper.get_max_frames(),console_width=progress.console.width)


        with open('controls.yaml', 'r') as file:
            controls = yaml.safe_load(file)

        controls_table = Table(show_edge=True,title_justify="left" ,show_header=False, box= box.ROUNDED)
        controls_table.add_column("Key", justify="right", style="dim cyan")
        controls_table.add_column("explanation", justify="left")
        for k,v in controls.items():
            controls_table.add_row(k, v)

        loop_table = Table(show_edge=True,title_justify="left" ,show_header=False, box= box.ROUNDED)
        loop_table.add_column("Property",justify="right")
        loop_table.add_column("Frame")
        loop_table.add_row("Start",str(102))
        loop_table.add_row("End",str(1214))
        loop_table.add_row("Length",str(1214-102))


        layout = Layout()
        controls = "controls"
        timeline = "timeline"
        info = "info"
        layout.split_column(
            Layout(name=timeline),
            Layout(name="lower")
        )
        layout["lower"].split_row(
            Layout(controls_table, name=controls),
            Layout(loop_table, name=info),
        )

        with Live(layout, screen=False) as live:
            for _ in range(40):
                time.sleep(0.4)
                live.update(self.generate_UI()) 
            # while True:
            #     pass
            #     progress.update(task1, completed=self.looper.get_current_frame())

                # time.sleep(0.05)


















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
