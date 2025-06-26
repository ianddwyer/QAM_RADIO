# -*- coding: utf-8 -*-
"""
Created on Wed May 28 22:40:12 2025

@author: Eian
"""

import sounddevice as sd
import soundfile as sf
import time

# Parameters
filename = 'music/Dr. Dre - The Next Episode (Wooli Flip).wav'
frame_size = 16  # Number of samples per frame

# Load audio file
audio_file = sf.SoundFile(filename)
samplerate = audio_file.samplerate
channels = audio_file.channels
dtype = 'float32'

# Real-time frame-by-frame playback
with sd.OutputStream(samplerate=samplerate, channels=channels, dtype=dtype) as stream:
    while True:
        data = audio_file.read(frames=frame_size, dtype=dtype)
        if len(data) == 0:
            break
        stream.write(data)  # Send frame to output in real-time
