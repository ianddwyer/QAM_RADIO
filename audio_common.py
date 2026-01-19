# audio_common.py
import struct

# UDP and Radio Parameters
UDP_IP = '127.0.0.1'
UDP_PORT = 5006
RADIO_RATE = 100000# The fixed byte-rate at which the "radio" operates
PACKET_SIZE_BYTES = 1024 # Fixed UDP packet size (min for 2ch audio is 400 bytes plus header for 2:1 in quick tests)

# Audio Data Type (using numpy/soundfile conventions)
AUDIO_DTYPE = 'float32'
BYTES_PER_SAMPLE = 4  # For float32, should be 2 bytes for int16, not really working 

# Header Structure (packed as a byte string)
# Format:
#   'I': unsigned int (4 bytes) for frame no
#   'H': unsigned short (2 bytes) for frame rate
#   'H': unsigned short (2 bytes) for channels
#   'I': unsigned int (4 bytes) for frame size(original audio frames per packet)
#   'B': unsigned char (1 byte) for dtype_code (e.g., 0 for float32)
# Total header size: 4 + 2 + 2 + 4 + 1 = 13 bytes

DTYPE_CODE_FLOAT32 = 0
DTYPE_MAP = {  DTYPE_CODE_FLOAT32: 'float32'}
REVERSE_DTYPE_MAP = { 'float32': DTYPE_CODE_FLOAT32}

#need to fix this to have 1024 bits with 16-byte header so get clean 252-byte packets
HEADER_FORMAT = '!fffHH' # ! for network byte order (big-endian)
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

# This calculates how many radio samples fit into the non-header part of a packet
RADIO_SAMPLES_PER_PACKET = (PACKET_SIZE_BYTES - HEADER_SIZE) // BYTES_PER_SAMPLE

RECEIVER_QUEUE_BUFFER_SECONDS =  1 #ensures a buffer equal to the packet size in seconds
RECEIVER_QUEUE_SIZE_PACKETS = int(RECEIVER_QUEUE_BUFFER_SECONDS * RADIO_RATE / RADIO_SAMPLES_PER_PACKET)

if RECEIVER_QUEUE_SIZE_PACKETS==0: RECEIVER_QUEUE_SIZE_PACKETS = 1 # Ensure at least one packet buffer