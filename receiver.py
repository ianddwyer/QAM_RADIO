import socket
import numpy as np
import sounddevice as sd
import threading
import queue
import time
from scipy.signal import resample_poly
import math



queue_size = 1024*8
audio_channels = 1 #initializer, pull from packet header
playback_rate = 44100 #initializer, pull from packet header
frame_size = 400 #initializer, pull from packet header
frame_num = 0 #frame number header, initializer, pull from packet header
strm_typ = 0 #stream type header, initializer, pull from packet header
ftype = 0 #file type header, initializer, pull from packet header

udp_ip = '0.0.0.0'
udp_port = 5005
packet_size_byte = 1024*8
packet_size_flt = packet_size_byte//4  # 4 bytes per float32 sample
radio_rate = 120000
dtype = 'float32'

payload = b''
MAX_PACKET_SIZE = 1024 * audio_channels * 4 * 3  # buffer room




def udp_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((udp_ip, udp_port))
    #print(f"Downsampling {radio_rate} Hz → {playback_rate} Hz | up_file={up_file}, down_file={down_file}")
    while True:
            payload, _ = sock.recvfrom(packet_size_byte)
            global playback_rate,frame_size,audio_channels,frame_num,strm_typ
            
            rate_head = payload[0:4] #obtain the playback rate from the packet header
            size_head = payload[4:8] #obtain the frame size in packet from the packet header (for checking for other frames appended in packet)
            chan_head = payload[8:9]  #obtain the audio channel count from the packet header
            fnum_head = payload[9:13] #obtain the frame number from the packet header
            styp_head = payload[13:14] #obtain the stream type from the packet header

            playback_rate = playback_rate.from_bytes(rate_head,byteorder='big')
            frame_size = frame_size.from_bytes(size_head,byteorder='big')
            audio_channels = audio_channels.from_bytes(chan_head,byteorder='big')
            frame_num = frame_num.from_bytes(fnum_head,byteorder='big')
            strm_typ = strm_typ.from_bytes(styp_head,byteorder='big')
            
            if strm_typ == 1 or strm_typ == 4:
                print(f"Stream Type: Audio")
                print(f"Frame Size: {frame_size} Bytes")
                print(f"Playback Rate: {playback_rate} Hz")
                print(f"Audio Channels: {audio_channels}")
            print("Payload: \n", payload[14:frame_size+14])

            radio_queue.put_nowait(payload)
            

def audio_callback(outdata, frames, time_info, status):
    try:
        global frame_size
        global playback_rate
        global payload
        global audio_channels
        
        # print("Channels:      ", channels)
        # print("Audio Rate:    ", playback_rate)
        # print("Frames(Bytes): ", audio_frame_size)
        # print(frames*8)
        payload = radio_queue.get_nowait()[13:frame_size+13]
        payload = np.frombuffer(payload, dtype=dtype).reshape(-1, audio_channels)
        
        
        gcd = math.gcd(playback_rate, radio_rate)
        up_file = playback_rate // gcd 
        down_file = radio_rate // gcd
        
        outdata[:] = payload
        #outdata[:] = resample_poly(payload, up_file, down_file, axis=0).astype(dtype)
        # print(len(resampled))
        
        # out_len = min(len(audio), audio_frame_size)
        
        # if out_len<frames: outdata[out_len:] = 0
    except queue.Empty:
        #print("Queue empty — inserting silence.")
        outdata.fill(0)

radio_queue = queue.Queue(maxsize=queue_size)
threading.Thread(target=udp_listener, daemon=True).start()

# Prebuffering
print("Waiting to buffer at least 10 frames...")
while radio_queue.qsize()<10: time.sleep(0.01)
print("Starting audio playback...")
with sd.OutputStream(samplerate=playback_rate, 
                     channels=audio_channels, 
                     dtype=dtype, 
                     blocksize=frame_size//8, 
                     callback=audio_callback):
    while True: time.sleep(0.1)
