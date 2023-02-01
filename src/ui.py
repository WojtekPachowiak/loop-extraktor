from rich.progress import Progress
from rich.progress_bar import ProgressBar
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TaskProgressColumn, MofNCompleteColumn, Task
from rich.table import Column
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.table import Table
from rich import box
from rich.layout import Layout
from rich.live import Live


from audio_master import AudioMaster
import threading
import time
import yaml

from log import Logger, error_handle



AUDIO_NOT_LOADED_MSG = "PRESS 'L' OR DRAG-N-DROP SOME .WAV FILE!"



class UI(threading.Thread):
    'Thread responsible for displaying in the console things such as frame count, controls instructions or current settings'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        

        #load controls instructions that will be displayed
        with open('controls.yaml', 'r') as file:
            self.controls = yaml.safe_load(file)

    @error_handle
    def run(self):
            self.audio_bar = Progress(AudioProgressColumn(justify="center"), expand=True)
            self.audio_bar.add_task("Audio timeline progress", console_width=self.audio_bar.console.width-6)

            self.setup_layout()
            self.draw_whole_layout()
            with Live(self.layout, refresh_per_second=100, screen=True) as live:
                while AudioMaster.is_running:
                    time.sleep(0.01)
                    self.draw_whole_layout()

 
#################### UI ELEMENTS ####################

    def setup_layout(self):
        'sets up all the TUI components that will be displayed in Live loop'

        #gather all the above defined elements into a common layout
        self.layout = Layout(name="root")
        self.layout.split(
            Layout(name="timeline",size=3),
            Layout(name="rest"),
            Layout(name="log", size=3)
        )
        self.layout["rest"].split_row(
            Layout(name="info"),
            Layout(name="controls")
        )

    def draw_whole_layout(self):
        self.draw_audio_info()
        self.draw_controls()
        self.draw_timeline()
        self.draw_log()



    def draw_controls(self):
        'draw table with info about controls'
        controls_table = Table(show_edge=True,show_header=False, box= box.ROUNDED, expand=True)
        controls_table.add_column(justify="right", style="dim cyan",ratio=1)
        controls_table.add_column(justify="left", ratio=3)
        for k,v in self.controls.items():
            controls_table.add_row(k, v)
        self.layout["controls"].update(controls_table)

    @error_handle
    def draw_timeline(self):
        'draw audio timeline'
        if AudioMaster.is_wav_loaded:
            Logger.log(f"Timeline is being updated: {AudioMaster.get_current_frame()} / {AudioMaster.get_max_frames()}")
            self.audio_bar.update(
                self.audio_bar.task_ids[0], 
                total=AudioMaster.get_max_frames(), 
                completed=AudioMaster.get_current_frame(), 
                console_width=self.audio_bar.console.width-6)
        self.layout["timeline"].update(Panel(self.audio_bar,expand=True, title=AudioMaster.filepath or "", title_align="left"))


    def draw_audio_info(self):
        'draw table with info about the loop'
        audio_table = Table(show_edge=True,show_header=False, box= box.ROUNDED, expand=True)
        audio_table.add_column(justify="right", style="cyan",ratio=1)
        audio_table.add_column(ratio=3)
    
        if AudioMaster.is_wav_loaded:
            audio_table.add_row("Start", f"{AudioMaster.LOOP_START:,}")
            audio_table.add_row("End", f"{AudioMaster.LOOP_END:,}")
            audio_table.add_row("Length", f"{AudioMaster.LOOP_END - AudioMaster.LOOP_START:,}")
            audio_table.add_section()
            audio_table.add_row("Frames", f"{AudioMaster.get_current_frame():,} / {AudioMaster.get_max_frames():,}")
            audio_table.add_row("Miliseconds",f"{AudioMaster.get_current_frame(ms_convert=True):,} / {AudioMaster.get_max_frames(ms_convert=True):,}")
            audio_table.add_row("Latency", f"{AudioMaster.get_output_latency():.4f}")
        else:
            audio_table.add_row("Start", "-" )
            audio_table.add_row("End", "-")
            audio_table.add_row("Length", "-")
            audio_table.add_section()
            audio_table.add_row("Frames", "-")
            audio_table.add_row("Miliseconds", "-")
            audio_table.add_row("Latency", "-")
        self.layout["info"].update(audio_table)

    def draw_log(self):
        'draw log with all the messages'
        self.layout["log"].update(Panel(Logger.LAST_ERROR_MSG or "", expand=True))

#################### CUSTOM COLUMNS ####################

class AudioProgressColumn(TextColumn):
    'custom progress bar column for displaying audio progress and a loop'
    
    bar = "█"
    indicator = "|"
    
    def __init__(self, text_format="", *args, **kwargs) -> None:
        super().__init__(text_format, *args, **kwargs)

    def render(self, task: Task) -> Text:
        'render the progress bar that will be displayed to the user'

        #if no audio is loaded, display a message
        if not AudioMaster.is_wav_loaded:
            return Text(AUDIO_NOT_LOADED_MSG, justify=self.justify,  style="bold red")
        else:
            width = task.fields["console_width"] + 1 # width of the console; +1 because of indicator
            ls = AudioMaster.LOOP_START
            le = AudioMaster.LOOP_END
            s = int(ls/task.total * width) # loop start pos
            e = int(le/task.total * width) #loop end pos
            _text = (
                AudioProgressColumn.bar * int(task.percentage/100 * width) + 
                AudioProgressColumn.indicator + 
                AudioProgressColumn.bar * int( (1.-task.percentage/100) * width)
            )
            text = Text(_text, justify=self.justify)
            text.stylize("bold blue", s, e) #stylize loop

            return text