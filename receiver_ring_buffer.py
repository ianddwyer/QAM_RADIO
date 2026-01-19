# audio_receiver.py
import socket
import numpy as np
import sounddevice as sd
import threading
import queue
import time
from scipy.signal import resample_poly
import math
import struct

from audio_common import (
    UDP_IP, UDP_PORT, RADIO_RATE, PACKET_SIZE_BYTES, AUDIO_DTYPE, BYTES_PER_SAMPLE,
    HEADER_FORMAT, HEADER_SIZE, RADIO_SAMPLES_PER_PACKET, DTYPE_MAP, RECEIVER_QUEUE_SIZE_PACKETS
)
UDP_PORT = 5007
# Global variables for audio playback configuration (initialized with defaults)
FILE_RATE = 44100 #init
CHANNELS = 1 #init
BLOCK_SIZE = 1024 # init
CURRENT_DTYPE = AUDIO_DTYPE
FRAME_NO = 0 # Frame number for tracking audio frames
last_data_packet = np.zeros((BLOCK_SIZE, CHANNELS), dtype=CURRENT_DTYPE) # Last received audio packet for debugging

# Queue to hold incoming radio packets before audio processing
radio_packet_queue = queue.Queue(maxsize=RECEIVER_QUEUE_SIZE_PACKETS)

# Lock for updating audio device parameters to prevent race conditions
audio_params_lock = threading.Lock()

# Flag to signal if audio device needs to be reconfigured
reconfigure_audio_device = threading.Event()

def udp_listener_thread():
    """Listens for UDP packets, parses them, and puts processed radio data into a queue."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    print(f"Receiver UDP Listener started on {UDP_IP}:{UDP_PORT}")

    global FILE_RATE, CHANNELS, FRAME_NO, BLOCK_SIZE, CURRENT_DTYPE, last_data_packet

    while True:
        try:
            packet, _ = sock.recvfrom(PACKET_SIZE_BYTES)

            if len(packet) != PACKET_SIZE_BYTES:
                print(f"Receiver UDP: Warning: Received packet size mismatch. Expected {PACKET_SIZE_BYTES}, got {len(packet)}")
                pass # This can happen if padding is not strict or due to network issues

            # Extract header
            if len(packet) < HEADER_SIZE:
                print("Receiver UDP: Error: Received packet too small to contain header.")
                continue
            #print(packet)
            ####THIS CURRENTLY PULLS THE HEADER FROM THE ALL RADIO PACKETS AND FRAMES, SO REALLY JUST AUDIO... NEED TO PROPERLY HANDLE THIS...
            header_bytes = packet[0:HEADER_SIZE]
            #print(header_bytes)
            try:
                (FRAME_NO, new_playback_rate, new_channels, new_audio_frame_size_samples, dtype_code) = struct.unpack(HEADER_FORMAT, header_bytes)
                new_dtype = DTYPE_MAP.get(dtype_code)
                if new_dtype is None:
                    print(f"Receiver UDP: Error: Unknown dtype code received: {dtype_code}. Skipping packet.")
                    continue

            except struct.error as e:
                print(f"Receiver UDP: Error unpacking header: {e}. Skipping packet.")
                continue

            # Extract audio data (radio samples)
            expected_payload_bytes = RADIO_SAMPLES_PER_PACKET * BYTES_PER_SAMPLE
            radio_data_bytes = packet[HEADER_SIZE : HEADER_SIZE + expected_payload_bytes]

            # Use new_dtype from header for correct interpretation
            radio_data = np.frombuffer(radio_data_bytes, dtype=new_dtype)
            #print(radio_data)
            #print(new_channels, new_playback_rate, new_audio_frame_size_samples, new_dtype)
            # Reshape to (frames, channels)
            radio_data = radio_data.reshape(-1, int(new_channels))
            

            # Check if audio parameters have changed and signal for reconfiguration
            #### THIS IS VERY WRONG, IT SHOULD NOT BE HERE, IT SHOULD BE IN THE AUDIO PLAYBACK THREAD
            with audio_params_lock:
                if (new_playback_rate != FILE_RATE or
                    new_channels != CHANNELS or
                    new_audio_frame_size_samples != BLOCK_SIZE or
                    new_dtype != CURRENT_DTYPE):

                    print(f"Receiver UDP: Detected new audio parameters. Old: Rate={FILE_RATE}, Ch={CHANNELS}, New: Rate={new_playback_rate}, Ch={new_channels}")
                    FILE_RATE = int(new_playback_rate)
                    CHANNELS = int(new_channels)
                    BLOCK_SIZE = int(new_audio_frame_size_samples)
                    CURRENT_DTYPE = (new_dtype)
                    reconfigure_audio_device.set() # Signal to reconfigure

            try: radio_packet_queue.put_nowait(radio_data) # Store the radio data (numpy array), not the raw packet bytes
            except queue.Full: pass # Drop oldest packet if queue is full (real-time system)
                
        except socket.error as e:
            print(f"Receiver UDP: Socket error in UDP listener: {e}")
            break
        except Exception as e:
            print(f"Receiver UDP: Unexpected error in UDP listener: {e}")
            break


def audio_playback_thread():
    """Manages the sound device stream and plays audio."""
    global FILE_RATE, CHANNELS, BLOCK_SIZE, CURRENT_DTYPE

    stream = None
    last_reconfigure_time = time.perf_counter()
    MIN_RECONFIGURE_INTERVAL_SECONDS = 0.5 # Prevents rapid reconfigs

    while True:
        # Check for reconfiguration signal
        if reconfigure_audio_device.is_set():
            # Debounce reconfiguration to avoid rapid restarts
            if time.perf_counter() - last_reconfigure_time < MIN_RECONFIGURE_INTERVAL_SECONDS:
                time.sleep(0.00001) # Wait a bit to let params settle
                continue

            with audio_params_lock:
                # Close existing stream if open
                if stream:
                    print("Receiver Audio: Closing existing audio stream...")
                    stream.stop() # Stop stream before closing
                    stream.close()
                    stream = None

                print(f"\nReceiver Audio: Reconfiguring audio playback:")
                print(f"  Sample Rate: {FILE_RATE} Hz")
                print(f"  Channels: {CHANNELS}")
                print(f"  Audio Frame Size (original frames per packet): {BLOCK_SIZE}")
                print(f"  Data Type: {CURRENT_DTYPE}")

                try:

                    if BLOCK_SIZE == 0: BLOCK_SIZE = 256 # Min reasonable block size

                    stream = sd.OutputStream(
                        samplerate=int(FILE_RATE),
                        channels=int(CHANNELS),
                        dtype=(CURRENT_DTYPE),
                        blocksize=int(BLOCK_SIZE), # Use a dynamic blocksize
                        callback=audio_callback
                    )
                    stream.start()
                    print("Receiver Audio: Audio stream started.")
                    reconfigure_audio_device.clear() # Clear the flag once configured
                    last_reconfigure_time = time.perf_counter()
                except sd.PortAudioError as e:
                    print(f"Receiver Audio: Error reconfiguring audio device: {e}. Retrying in 1 second...")
                    reconfigure_audio_device.set() # Keep the flag set to try again
                    time.sleep(0.00001)
                except Exception as e:
                    print(f"Receiver Audio: Unexpected error during audio stream setup: {e}")
                    reconfigure_audio_device.set() # Keep the flag set to try again
                    time.sleep(0.00001)
            continue # Go back to the top of the loop to check for more data or reconfiguration

        # Small sleep to prevent busy-waiting if stream is not active/configured yet
        if not stream or not stream.active:
            time.sleep(0.00001)
            continue

        time.sleep(0.00001) # Keep thread responsive, but yield CPU

def audio_callback(outdata, frames, time_info, status):
    """Callback function for sounddevice to fill audio buffer."""
    global FILE_RATE, CHANNELS, BLOCK_SIZE, CURRENT_DTYPE, last_data_packet

    if status:  print(f"Receiver Callback Status: {status}")

    try:
        # Get radio data from the queue
        radio_data_packet = radio_packet_queue.get_nowait()

        # Sanity check on the received radio_data_packet shape
        # if radio_data_packet.shape[1] != CHANNELS:
        #     print(f"Receiver Callback: Warning! Channel mismatch in received radio data. Expected {CHANNELS}, got {radio_data_packet.shape[1]}. Attempting to reshape.")
        #     # This might lead to corrupted audio but prevents errors if channels mismatch.
        #     radio_data_packet = radio_data_packet.reshape(-1, CHANNELS)

        # Resample from RADIO_RATE back to FILE_RATE
        gcd_val = math.gcd(int(FILE_RATE), int(RADIO_RATE))
        up_ratio = FILE_RATE // gcd_val
        down_ratio = RADIO_RATE // gcd_val
        resampled_audio = resample_poly(radio_data_packet, 1, 1, axis=0).astype(CURRENT_DTYPE)
        #print(resampled_audio)
        #resampled_audio = resampled_audio*2-1
        # Ensure `resampled_audio` has enough samples to fill `outdata`
        # `outdata` expects `frames` samples per channel.
        if resampled_audio.shape[0]>=frames: 
            outdata[:]=resampled_audio[:frames, :].astype(CURRENT_DTYPE)
            last_data_packet = resampled_audio[:frames, :].astype(CURRENT_DTYPE) # Store the last received packet for debugging
        else:
            # Not enough data from this packet for the requested 'frames'
            print(f"Receiver Callback: UNDERRUN - Not enough resampled audio data ({resampled_audio.shape[0]}) for callback frames ({frames}). Filling with zeros.")
            last_data_packet = resampled_audio.astype(CURRENT_DTYPE) # Store the last received packet for debugging
            outdata[:resampled_audio.shape[0], :] = resampled_audio.astype(CURRENT_DTYPE)
            outdata[resampled_audio.shape[0]:, :] = 0 # Fill remaining with silence
        #print(outdata[:])
        #last_data_packet = outdata[:]

    except queue.Empty:
        # This is a common underrun scenario for real-time.
        # print("Receiver Callback: Audio queue empty — inserting silence.")
        outdata.fill(0)
    except Exception as e:
        print(f"Receiver Callback: Error in audio callback: {e}")
        outdata.fill(0) # Fill with silence on error


if __name__ == "__main__":
    print("Starting audio receiver...")
    # Start the UDP listener thread
    listener_thread = threading.Thread(target=udp_listener_thread, daemon=True)
    listener_thread.start()

    # Start the audio playback thread
    playback_thread = threading.Thread(target=audio_playback_thread, daemon=True)
    playback_thread.start()

    # Initial buffer fill check: wait for some packets to arrive
    print("Receiver: Waiting for first audio packet to configure playback device and buffer...")
    # Wait until at least 1 packet is in the queue, or a timeout.
    start_time = time.perf_counter()
    while radio_packet_queue.qsize() < 1 and listener_thread.is_alive():
        if time.perf_counter() - start_time > 5: # Timeout after 5 seconds
            print("Receiver: Timeout waiting for first packet. Starting with default settings.")
            break
        time.sleep(0.00001)

    if radio_packet_queue.qsize()>=1: reconfigure_audio_device.set() # Trigger initial configuration with first packet's data

    try:
        while True: time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt: print("Receiver stopped.")
    finally:
        # Clean up sounddevice streams if they are still active
        print(last_data_packet)
        print(last_data_packet.shape)
        sd.stop()
        sd._terminate()