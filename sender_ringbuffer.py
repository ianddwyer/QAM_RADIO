# audio_sender.py
import socket
import soundfile as sf
import time
import numpy as np
from scipy.signal import resample_poly
import math
import struct
import threading
# queue is no longer needed here as we are using a ring buffer

from audio_common import (
    UDP_IP, UDP_PORT, RADIO_RATE, PACKET_SIZE_BYTES, AUDIO_DTYPE, BYTES_PER_SAMPLE,
    HEADER_FORMAT, HEADER_SIZE, RADIO_SAMPLES_PER_PACKET,
    DTYPE_CODE_FLOAT32, REVERSE_DTYPE_MAP # Ensure REVERSE_DTYPE_MAP is imported
)
UDP_PORT = 5006
last_data_packet = []
# --- RING BUFFER SETUP ---
# Size of the ring buffer in *total radio samples* (across all channels).
# It's good to buffer a few seconds.
# RADIO_RATE * BYTES_PER_SAMPLE is bytes/sec.
# RADIO_RATE * BUFFER_DURATION_SECONDS gives total samples for that duration (mono).
# We store flattened data (total samples across all channels).
BUFFER_DURATION_SECONDS =  1 #ensures a buffer equal to the packet size in seconds
RING_BUFFER_TOTAL_SAMPLES_CAPACITY = int(RADIO_RATE * BUFFER_DURATION_SECONDS * 2) # Times 2 for stereo support (worst case for mono data in buffer)
# Make sure this is a multiple of RADIO_SAMPLES_PER_PACKET for easier logic later.
# Add some padding to ensure it's slightly larger than an exact multiple.
RING_BUFFER_TOTAL_SAMPLES_CAPACITY = (RING_BUFFER_TOTAL_SAMPLES_CAPACITY // RADIO_SAMPLES_PER_PACKET + 1) * RADIO_SAMPLES_PER_PACKET

RING_BUFFER = np.zeros(RING_BUFFER_TOTAL_SAMPLES_CAPACITY, dtype=AUDIO_DTYPE)

write_ptr = 0 # Points to where the next sample should be written (index in RING_BUFFER)
read_ptr = 0  # Points to where the next sample should be read (index in RING_BUFFER)
samples_in_buffer = 0 # Number of samples currently available for reading

# Condition variables for synchronization
# buffer_lock: Protects access to RING_BUFFER, write_ptr, read_ptr, samples_in_buffer
# reader_can_read: Reader waits on this if buffer is empty
# writer_can_write: Writer waits on this if buffer is full
buffer_lock = threading.Lock()
reader_can_read = threading.Condition(buffer_lock)
writer_can_write = threading.Condition(buffer_lock)
# --- END RING BUFFER SETUP ---

# Audio file to send
AUDIO_FILE = 'music/Dr. Dre - The Next Episode (Wooli Flip).wav' # Make sure this path is correct

def audio_reader_thread():
    """Reads audio file, resamples, and writes processed radio data to the ring buffer."""
    global write_ptr, samples_in_buffer, last_data_packet

    # Read audio file properties once for header and resampling setup
    with sf.SoundFile(AUDIO_FILE, 'r') as f_info:
        FILE_RATE = f_info.samplerate
        CHANNELS = f_info.channels
        # Pre-calculate common header info
        gcd_val = math.gcd(RADIO_RATE, FILE_RATE)
        up_ratio = RADIO_RATE // gcd_val
        down_ratio = FILE_RATE // gcd_val
        RADIO_FRPERCH = RADIO_SAMPLES_PER_PACKET // CHANNELS
        # Calculate how many original audio frames are needed to produce radio frames per channel
        FRAME_SIZE = max(1, int(RADIO_FRPERCH * down_ratio / up_ratio))

    print(f"Sender Audio File: {AUDIO_FILE}")
    print(f"Sender File Rate: {FILE_RATE} Hz, Channels: {CHANNELS}, Dtype: {AUDIO_DTYPE}")
    print(f"Sender Radio Rate: {RADIO_RATE} Hz, Packet Size: {PACKET_SIZE_BYTES} bytes")
    print(f"Sender Header Size: {HEADER_SIZE} bytes")
    print(f"Sender Radio Samples per Packet (payload): {RADIO_SAMPLES_PER_PACKET}")
    print(f"Sender Calculated audio frames to read per cycle: {FRAME_SIZE}")
    print(f"Sender Resampling: Original {FILE_RATE} Hz ({down_ratio}) -> Radio {RADIO_RATE} Hz ({up_ratio})")
    print(f"Sender Ring Buffer Capacity: {RING_BUFFER_TOTAL_SAMPLES_CAPACITY} samples ({BUFFER_DURATION_SECONDS:.2f} seconds)")

    # The actual number of flattened samples this thread will produce per cycle
    # This must match RADIO_SSAMPLES_PER_PACKET for simple ring buffer logic.
    radio_samples_produced_per_cycle = RADIO_SAMPLES_PER_PACKET

    
    with sf.SoundFile(AUDIO_FILE, 'r') as f:
        count = 0 # For debugging, to track how many frames we read
        while True:
            data = f.read(frames=FRAME_SIZE, dtype=AUDIO_DTYPE, always_2d=True)
            #data = (data+1)/2
            last_data_packet = data
            if not data.any() and count > 1000:
                print("Sender: End of audio file. Looping...")
                f.seek(0)
                count = 0
                continue
            count += 1
            count = count % 1e6 # Prevent overflow in count
            # Handle partial reads at end of file by padding
            if len(data) < FRAME_SIZE:
                padded_data = np.zeros((FRAME_SIZE, CHANNELS), dtype=AUDIO_DTYPE)
                padded_data[:len(data)] = data
                data = padded_data

            # Resample audio data to radio rate
            #####THIS IS THE MOST WRONG PART, THE AUDIO FRAMES ARE ONLY PART OF THE ENTIRE RADIO PACKET, NOT THE ENTIRE PACKET
            #####THE METHOD SHOULD FILL ONLY FILL THE PACKET RELATIVE TO AUDIO FREQUENCY REQUIREMENTS RELATIVE TO THE RADIO'S RATE
            #####CHANGED TO NO RESAMPLE SO IT ZERO-FILLS FOR OTHER DATA TO FIT INTO THE PACKET
            resampled_data = resample_poly(data, 1, 1, axis=0).astype(AUDIO_DTYPE)

            # Ensure the resampled data has the exact expected number of samples (per channel)
            if resampled_data.shape[0] != RADIO_FRPERCH:
                if resampled_data.shape[0]>RADIO_FRPERCH:  resampled_data = resampled_data[:RADIO_FRPERCH, :]
                else: # Pad with zeros if too short
                    temp_padded = np.zeros((RADIO_FRPERCH, CHANNELS), dtype=AUDIO_DTYPE)
                    temp_padded[:resampled_data.shape[0], :] = resampled_data
                    resampled_data = temp_padded

            # Flatten the resampled data for linear storage in the ring buffer
            resampled_flat_bytes = resampled_data.tobytes()
            # Convert back to numpy array of the correct dtype for writing
            np_resampled_flat = np.frombuffer(resampled_flat_bytes, dtype=AUDIO_DTYPE)

            # --- Write to Ring Buffer ---
            with buffer_lock:
                # Wait if not enough space in the buffer for the next chunk
                while (RING_BUFFER_TOTAL_SAMPLES_CAPACITY - samples_in_buffer) < radio_samples_produced_per_cycle:
                    # print("Sender Reader: Buffer full, waiting for UDP sender to consume...")
                    writer_can_write.wait() # Writer sleeps here

                # Calculate available space from write_ptr to end of buffer
                space_to_end = RING_BUFFER_TOTAL_SAMPLES_CAPACITY - write_ptr

                if len(np_resampled_flat) > space_to_end:
                    # Data wraps around: write to end, then from beginning
                    RING_BUFFER[write_ptr:RING_BUFFER_TOTAL_SAMPLES_CAPACITY] = np_resampled_flat[:space_to_end]
                    RING_BUFFER[0 : len(np_resampled_flat) - space_to_end] = np_resampled_flat[space_to_end:]
                else: RING_BUFFER[write_ptr : write_ptr + len(np_resampled_flat)] = np_resampled_flat # Data fits in one go

                write_ptr = (write_ptr + len(np_resampled_flat)) % RING_BUFFER_TOTAL_SAMPLES_CAPACITY
                samples_in_buffer += len(np_resampled_flat)

                # Notify the UDP sender that new data is available
                #reader_can_read.notify_all() #<-REMOVED SINCE THE READER SHOULD BE ABLE TO PULL ANY VALUE AT RATE
            # --- End Write to Ring Buffer ---


def udp_sender_thread():
    """Reads processed radio data from the ring buffer, forms packets, and sends over UDP."""
    global read_ptr, samples_in_buffer

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Pre-calculate header and packet structure once
    #### THIS SHOULD NOT BE HANDLED IN THE UDP SENDER, ONLY IN THE AUDIO READERS PACKETIZING SECTION
    with sf.SoundFile(AUDIO_FILE, 'r') as f_info:
        FILE_RATE = f_info.samplerate
        CHANNELS = f_info.channels
        gcd_val = math.gcd(RADIO_RATE, FILE_RATE)
        up_ratio = RADIO_RATE // gcd_val
        down_ratio = FILE_RATE // gcd_val
        RADIO_FRPERCH = RADIO_SAMPLES_PER_PACKET // CHANNELS
        FRAMES_SIZE = max(1, int(RADIO_FRPERCH * down_ratio / up_ratio))

    
    # The payload size is fixed by RADIO_SAMPLES_PER_PACKET * BYTES_PER_SAMPLE
    payload_data_len_bytes = RADIO_SAMPLES_PER_PACKET * BYTES_PER_SAMPLE
    print(payload_data_len_bytes)
    # Packet send period based on radio rate
    #### THIS IS VERY WRONG, THE RADIO PACKET PERIOD SHOULD NOT BE DEPENDENT ON THE CHANNELS, ONLY THE AUDIO FRAMES PER PACKET
    PACKET_SIZE_BYTES = HEADER_SIZE + payload_data_len_bytes
    packet_period = RADIO_SAMPLES_PER_PACKET / RADIO_RATE / CHANNELS
    print(f"Sender: Sending a UDP packet every {packet_period:.6f} seconds.")

    next_send_time = time.perf_counter()

    FRAME_NO = 0
    while True:
        payload_data_for_packet = None # Will hold the numpy array chunk for the current packet
        samples_consumed_from_buffer = 0

        # --- Read from Ring Buffer ---
        with buffer_lock:
            # Wait if not enough data is available for a full packet
            while samples_in_buffer < RADIO_SAMPLES_PER_PACKET:
                # print("Sender UDP: Buffer empty, waiting for audio reader...")
                # Add a timeout to prevent indefinite wait if reader stops
                # If timeout occurs, it means underrun, send silence
                if not reader_can_read.wait(timeout=packet_period * 1): # Wait up to 2 packet periods
                    #print("Sender UDP: UNDERRUN - Buffer not filling fast enough. Sending silence.")
                    payload_data_for_packet = np.zeros(RADIO_SAMPLES_PER_PACKET, dtype=AUDIO_DTYPE)
                    samples_consumed_from_buffer = 0 # No actual samples consumed
                    break # Break out of inner while loop

            if payload_data_for_packet is None: # Only if we successfully waited/had data
                # Read from the ring buffer
                data_to_end = RING_BUFFER_TOTAL_SAMPLES_CAPACITY - read_ptr
                if RADIO_SAMPLES_PER_PACKET > data_to_end:
                    # Data wraps around: read to end, then from beginning
                    part1 = RING_BUFFER[read_ptr:RING_BUFFER_TOTAL_SAMPLES_CAPACITY]
                    part2 = RING_BUFFER[0 : RADIO_SAMPLES_PER_PACKET - data_to_end]
                    payload_data_for_packet = np.concatenate((part1, part2))
                else: payload_data_for_packet = RING_BUFFER[read_ptr : read_ptr + RADIO_SAMPLES_PER_PACKET]# Data fits in one go

                read_ptr = (read_ptr + RADIO_SAMPLES_PER_PACKET) % RING_BUFFER_TOTAL_SAMPLES_CAPACITY
                samples_in_buffer -= RADIO_SAMPLES_PER_PACKET
                samples_consumed_from_buffer = RADIO_SAMPLES_PER_PACKET

            # Notify the audio reader that space is now available in the buffer
            if samples_consumed_from_buffer>0: writer_can_write.notify_all() # Only notify if we actually consumed
                
        # --- End Read from Ring Buffer ---

        # Construct the final UDP packet
        header = struct.pack(
            HEADER_FORMAT,
            FRAME_NO,
            FILE_RATE,
            CHANNELS,
            FRAMES_SIZE,
            REVERSE_DTYPE_MAP[AUDIO_DTYPE]
        )
        FRAME_NO += 1
        packet_to_send = header + payload_data_for_packet.tobytes()

        #print(payload_data_for_packet.tobytes())

        # Pad the packet to the fixed UDP_PACKET_SIZE_BYTES if necessary
        if len(packet_to_send)>PACKET_SIZE_BYTES:
            #print(f"Sender UDP: Error - Final packet size ({len(packet_to_send)}) exceeds max allowed ({PACKET_SIZE_BYTES}). Truncating.")
            packet_to_send = packet_to_send[:PACKET_SIZE_BYTES]
        elif len(packet_to_send)<PACKET_SIZE_BYTES:  packet_to_send = packet_to_send.ljust(PACKET_SIZE_BYTES, b'\x00')

        sock.sendto(packet_to_send, (UDP_IP, UDP_PORT))

        # --- Timing for real-time sending ---
        next_send_time += packet_period
        now = time.perf_counter()
        sleep_time = next_send_time - now

        if sleep_time > 0: time.sleep(sleep_time)
        # else:
        #     # If we're behind, adjust next_send_time to catch up but warn
        #     # if abs(sleep_time)>packet_period*0.1: print(f"Sender UDP: WARNING - Timing Error of {-sleep_time:.6f}s.") # Warn if more than 10% behind   
        #     next_send_time = now # Reset to current time to try and get back on track

if __name__ == "__main__":
    print("Starting audio sender (Ring Buffer version)...")
    reader_thread = threading.Thread(target=audio_reader_thread, daemon=True)
    reader_thread.start()

    sender_thread = threading.Thread(target=udp_sender_thread, daemon=True)
    sender_thread.start()

    try:
        while True: time.sleep(1) # Keep main thread alive
    except KeyboardInterrupt: 
        print(last_data_packet)
        print(last_data_packet.shape)
        print("Sender stopped.")