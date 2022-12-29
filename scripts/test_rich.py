from rich import print
from rich.console import Group
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich import box
import yaml

from rich import print
from rich.layout import Layout




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


timeline_char = '█ '
Panel("Hello", title="siema",title_align="left",expand=True)

# panel_group = Group(
#     Panel("Hello", title="siema",title_align="left",expand=True),
#     Panel(
#         "s", 
#         title="Controls"
#         ),
# )
# print(Panel(panel_group))

# from rich.console import Console
# from rich.theme import Theme
# custom_theme = Theme({
#     "info": "dim cyan",
#     "warning": "magenta",
#     "danger": "bold red"
# })
console = Console()
# console.print("This is information", style="info")
# console.print("[warning]The pod bay doors are locked[/warning]")
# console.print("Something terrible happened!", style="danger")


#############
from rich.text import Text


layout = Layout()

controls = "controls"
timeline = "timeline"
info = "info"

layout.split_column(
    Layout(timeline_char * 80, name=timeline),
    Layout(name="lower")
)
layout["lower"].split_row(
    Layout(controls_table, name=controls),
    Layout(loop_table, name=info),
)

###########



from rich.live import Live
from rich.table import Table
import random
import time

def generate_table(size = 0) -> Table:
    layout = Layout(size =1)

    controls = "controls"
    timeline = "timeline"
    info = "info"

    panel = Panel("a")
    
    panel.renderable = Text(timeline_char*(size//2))
    layout.split_column(
        Layout(panel,name=timeline),
        Layout(name="lower")
    )
    layout["lower"].split_row(
        Layout(controls_table, name=controls),
        Layout(loop_table, name=info),
    )
    # print(size)
    return layout


with Live(generate_table(), refresh_per_second=4, screen=False) as live:
    for _ in range(40):
        time.sleep(0.4)
        
        live.update(generate_table(live.console.size.width-4)) 
