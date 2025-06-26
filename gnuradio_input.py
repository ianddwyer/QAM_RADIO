# -*- coding: utf-8 -*-
"""
Created on Mon May  5 07:19:47 2025

@author: Eian
"""

import socket
import argparse
import subprocess
import numpy as np
import time
import sys
import os

def load_input_data(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".wav":
        import soundfile as sf
        data, rate = sf.read(file_path, dtype='float32')
        if data.ndim > 1:
            data = data[:, 0]
        return data, rate
    elif ext == ".bin":
        data = np.fromfile(file_path, dtype=np.uint8)
        return data.astype(np.float32), 1_000_000  # default 1 MHz for raw
    else:
        raise ValueError("Unsupported file format.")

def upsample(data, in_rate, out_rate):
    import resampy
    return resampy.resample(data, in_rate, out_rate)

def stream_udp(data, rate, ip, port, chunk_size=1024):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    total_chunks = int(np.ceil(len(data) / chunk_size))
    data = np.pad(data, (0, total_chunks * chunk_size - len(data)))
    print(f"[Streaming to {ip}:{port} at {rate} Hz]")

    for i in range(total_chunks):
        chunk = data[i * chunk_size : (i + 1) * chunk_size]
        sock.sendto(chunk.tobytes(), (ip, port))
        time.sleep(chunk_size / rate)

def launch_gnuradio(script_path, ip, port):
    print(f"[Launching GNU Radio script: {script_path}]")
    subprocess.Popen([sys.executable, script_path,
                      f"--udp_ip={ip}", f"--udp_port={port}"])

def main():
    parser = argparse.ArgumentParser(description="UDP Streamer + GNU Radio Launcher")
    parser.add_argument("--input", required=True, help="Input file path (.wav or .bin)")
    parser.add_argument("--udp_ip", default="127.0.0.1", help="Destination IP")
    parser.add_argument("--udp_port", type=int, default=5005, help="Destination port")
    parser.add_argument("--out_rate", type=int, default=48000, help="Output rate (Hz)")
    parser.add_argument("--radio_script", required=True, help="GNU Radio Python script")

    args = parser.parse_args()

    # Load and resample
    data, in_rate = load_input_data(args.input)
    print(f"[Loaded {args.input} at {in_rate} Hz]")
    if in_rate != args.out_rate:
        print(f"[Resampling to {args.out_rate} Hz]")
        data = upsample(data, in_rate, args.out_rate)

    # Launch GNU Radio receiver
    launch_gnuradio(args.radio_script, args.udp_ip, args.udp_port)

    # Stream to UDP
    stream_udp(data, args.out_rate, args.udp_ip, args.udp_port)

if __name__ == "__main__":
    main()
