# -*- coding: utf-8 -*-
"""
Created on Sat May 10 02:07:51 2025

@author: Eian
"""

import socket
import numpy as np
import pyaudio
from scipy.signal import resample_poly

# === CONFIGURABLE ===
UDP_IP = "127.0.0.1"
UDP_PORT = 5007
UDP_SAMPLE_RATE = 48000     # Incoming rate (e.g., 8 kHz)
PLAYBACK_SAMPLE_RATE = 48000  # Playback rate (e.g., 44.1 kHz)
CHUNK_SIZE = 16           # Size of incoming packets (in bytes)
CHANNELS = 1
FORMAT = pyaudio.paInt16   # Assumes 16-bit signed PCM

# === SOCKET SETUP ===
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

# === PY AUDIO SETUP ===
p = pyaudio.PyAudio()
stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=PLAYBACK_SAMPLE_RATE,
                output=True)

# === RESAMPLE RATIO ===
gcd = np.gcd(PLAYBACK_SAMPLE_RATE, UDP_SAMPLE_RATE)
up = PLAYBACK_SAMPLE_RATE // gcd
down = UDP_SAMPLE_RATE // gcd

print(f"Resampling incoming audio from {UDP_SAMPLE_RATE} Hz to {PLAYBACK_SAMPLE_RATE} Hz")

try:
    while True:
        data, _ = sock.recvfrom(CHUNK_SIZE)
        samples = np.frombuffer(data, dtype=np.int16)
        resampled = resample_poly(samples, up, down)
        stream.write(resampled.astype(np.int16).tobytes())
except KeyboardInterrupt:
    pass
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()
    sock.close()
