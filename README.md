# `loop-extraktor` - creatively loop .wav file's audio segments (for experimentation and fun!)

## Video example

[![Watch the video](https://img.youtube.com/vi/CoHniw9phoA/maxresdefault.jpg)](https://youtu.be/CoHniw9phoA)

(note that there's mistake in controls panel: `LEFT_ARROW` moves the loop to the left and `UP_ARROW` speeds up playback)

## Features
- moving loop (`left/right arrows`)
- resizing loop (`]``[`)
- randomly placing loop (`SPACE`)
- saving audio in the loop as .wav (`S`)
- pause/unpause (`P`)
- load new audio whenever you want (`L`)
- slowdown/speedup audio playback (`up/down arrows`)

## Usage

`src\main.py -o <where-you-want-to-save-audio-when-pressing-S> (--log)` \
`--log` enables logging for debugging purposes

For example run: \
`src\main.py -o .\saved_audio\` 


## TODO (Contrubtions welcome)
- Switch to `pedalboard`'s `AudioFile` for opening files other than `.wav`
- (SUSPENDED; not sure if it can be made efficient in Python) Implement applying audio effects real-time (delay, reverb, pitch shift, etc.) and arppeggio 
- Load audio files by drag and drop
- (SUSPENDED; working with Rich TUI is a pain in the ass for proper error handling) error handle to prevent crashes when, for example, opening non-wav files
-  (SUSPENDED; working with Rich TUI is a pain in the ass for proper error handling) Print errors in UI instead of logs
- modify SEEK speed by pressing SHIFT or CTRL
- change loop position by clicking on progress bar
