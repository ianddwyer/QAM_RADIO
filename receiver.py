import socket
import numpy as np
import sounddevice as sd
import threading
import queue
import time
from scipy.signal import resample_poly
import math

udp_ip = '0.0.0.0'
udp_port = 5005
frame_size = 1024
radio_rate = 125000
channels = 2
playback_rate = 48000
dtype = 'float32'
MAX_PACKET_SIZE = frame_size * channels * 4 * 3  # buffer room
queue_size = 1024*8

gcd = math.gcd(playback_rate, radio_rate)
up = playback_rate // gcd
down = radio_rate // gcd

audio_queue = queue.Queue(maxsize=queue_size)

def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    print(f"Downsampling {radio_rate} Hz → {playback_rate} Hz | up={up}, down={down}")
    while True:
        try:
            data_bytes, _ = sock.recvfrom(MAX_PACKET_SIZE)
            frame = np.frombuffer(data_bytes, dtype=dtype).reshape(-1, channels)
            resampled = resample_poly(frame, up, down, axis=0).astype(dtype)
            audio_queue.put_nowait(resampled)
        except queue.Full:
            print("Queue full — dropping frame.")
        except Exception as e:
            print("Listener error:", e)

threading.Thread(target=udp_listener, daemon=True).start()

def audio_callback(outdata, frames, time_info, status):
    try:
        frame = audio_queue.get_nowait()
        out_len = min(len(frame), frames)
        outdata[:out_len] = frame[:out_len]
        if out_len < frames:
            outdata[out_len:] = 0
    except queue.Empty:
        print("Queue empty — inserting silence.")
        outdata.fill(0)

# Prebuffering
print("Waiting to buffer at least 10 frames...")
while audio_queue.qsize() < 10:
    time.sleep(0.01)

print("Starting audio playback...")
with sd.OutputStream(samplerate=playback_rate, channels=channels, dtype=dtype,
                     blocksize=frame_size, callback=audio_callback):
    while True:
        time.sleep(0.1)
