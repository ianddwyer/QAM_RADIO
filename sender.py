import socket
import soundfile as sf
import time
import numpy as np
from scipy.signal import resample_poly
import math

udp_ip = '127.0.0.1'
udp_port = 5005
frame_size = 1024
dtype = 'float32'

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

with sf.SoundFile('music/Dr. Dre - The Next Episode (Wooli Flip).wav') as f:
    file_rate = f.samplerate
    channels = f.channels
    radio_rate = 125000  # modulation rate
    gcd = math.gcd(radio_rate, file_rate)
    up = radio_rate // gcd
    down = file_rate // gcd

    interval = frame_size / radio_rate  # seconds per frame
    print(f"Upsampling {file_rate} Hz → {radio_rate} Hz | up={up}, down={down}")
    
    next_time = time.perf_counter()

    while True:
        data = f.read(frames=frame_size, dtype=dtype, always_2d=True)
        if len(data) == 0:
            break

        resampled = resample_poly(data, up, down, axis=0).astype(dtype)
        sock.sendto(resampled.tobytes(), (udp_ip, udp_port))

        next_time += interval
        now = time.perf_counter()
        sleep_time = next_time - now
        if sleep_time > 0:
            time.sleep(sleep_time)
        else:
            next_time = now
