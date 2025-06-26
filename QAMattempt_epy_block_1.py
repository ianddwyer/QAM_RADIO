
import numpy as np
from gnuradio import gr
import pmt

class DropByteToMessage(gr.basic_block):
    def __init__(self, dropvalue=0xFF):
        gr.basic_block.__init__(
            self,
            name="Drop Null",
            in_sig=[np.uint8],   # Stream input (bytes)
            out_sig=None         # Message output init will null
        )
        self.message_port_register_out(pmt.intern("out"))  # Create message output port

    def general_work(self, input_items, output_items):
        # Filter out the unwanted byte
        filtereddata = [x for x in input_items[0] if x != 0]
        
        if filtereddata:  # If there's valid data after filtering
            msg = pmt.init_u8vector(len(filtereddata), filtereddata)  # Convert to PMT message
            self.message_port_pub(pmt.intern("out"), msg)  # Send the message
        
        self.consume(0, len(input_items[0]))  # Consume all input samples
        return 0  # No output samples in streaming mode (only messages), not a standard zero return
