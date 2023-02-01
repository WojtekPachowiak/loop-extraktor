# loop-extraktor - looping random segments from an audio track (for experimentation and fun!)

Based on the following gist: https://gist.github.com/THeK3nger/3624478
from [THeK3nger](https://github.com/THeK3nger)

# Loop audio files starting in random places and with adjustable loop interval

# TODO (Contrubtions welcome)
- Switch to `pedalboard`'s `AudioFile` for opening files
- (SUSPENDED; not sure if it can be made efficient in Python) Implement applying audio effects real-time (delay, reverb, pitch shift, etc.) and arppeggio 
- Load audio files by drag and drop
- (SUSPENDED; working with Rich TUI is a pain in the ass for proper error handling) error handle to prevent crashes when, for example, opening non-wav files
-  (SUSPENDED; working with Rich TUI is a pain in the ass for proper error handling) Print errors in UI instead of logs
