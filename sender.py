import socket
import soundfile as sf
import time
import numpy as np
from scipy.signal import resample_poly
import math
import struct

udp_ip = '127.0.0.1'
udp_port = 5005
packet_size_byte = 1024*8
packet_size_flt = packet_size_byte // 4  # 4 bytes per float32 sample
radio_rate = 120000  # modulation rate
dtype = 'float32'

TYPE_REQST = 0 #push-pull request between users
TYPE_AUDIO = 1 #audio data
TYPE_MESSG = 2 #message as text stream
TYPE_FTRAN = 3 #file tranfer
TYPE_VIDEO = 4 #video if possible

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    with sf.SoundFile('music/Dr. Dre - The Next Episode (Wooli Flip).wav') as f:
        file_rate = f.samplerate
        channels = f.channels
        
        gcd = math.gcd(radio_rate, file_rate)
        up_file = radio_rate // gcd
        down_file = file_rate // gcd
        
        audio_frame_sz = packet_size_flt//channels * file_rate//radio_rate #pulling the packet size if sampled at rate will automatically fill this size
        audio_frame_sz_bytes = audio_frame_sz*4*channels # 4 bytes per float32 channel
        
        radio_period = packet_size_byte / radio_rate  # seconds per frame
        print(f"Upsampling {file_rate} Hz → {radio_rate} Hz | up_file={up_file}, down_file={down_file}")
        
        next_time = time.perf_counter()
        count = 0
        while True:
            data = f.read(frames= audio_frame_sz, dtype=dtype, always_2d=True).astype(dtype).tobytes()
            # if sum(struct.unpack('f' *(audio_frame_sz_bytes), data))==0 and count==100: break
            # count +=1 #counts to stall the end of song break, dev only, use separate app for handing audio and when to break stream with continue header flag
            # data = resample_poly(data, up_file, down_file, axis=0).astype(dtype).tobytes() #fixes 0's between data due to lower sample rate of audio
            print("Payload: \n",data)
            data = TYPE_AUDIO.to_bytes(1,byteorder='big') + data #append the stream type for handlin
            frame_no = count.to_bytes(4, byteorder='big')
            data = frame_no + data #append the frame number for better real-time handling and error tracking
            count += 1 #step the frame number for next packet
            len_payload = audio_frame_sz_bytes
            data = channels.to_bytes(1,byteorder='big') + data
            size_head = len_payload.to_bytes(4,byteorder='big') #16-bit, 2-byte payload len header
            data = size_head+data
            data = data.ljust(audio_frame_sz_bytes, b'\x00')
            rate_head =  file_rate.to_bytes(4,byteorder='big') #32-bit, 4-byte rate header, data starts at byte 5 
            data = rate_head+data
            len_frame = len(data) #total length for debug reference
            data = data.ljust(packet_size_byte, b'\x00') # Zero-pad if too short
            len_packet = len(data)

            print(len_packet)
            
            
            
            sock.sendto(data, (udp_ip, udp_port))
    
            next_time += radio_period
            now = time.perf_counter()
            sleep_time = next_time - now
            if sleep_time > 0: time.sleep(sleep_time)
            else: next_time = now
