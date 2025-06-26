# -*- coding: utf-8 -*-
"""
Created on Thu Apr 17 10:31:17 2025

@author: Eian
"""

import numpy as np
from gnuradio import gr
import pmt
import sys  

class print_message_block(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self,
            name="Print to Console",
            in_sig=None,
            out_sig=None)  # No output signal needed

        # register message input port
        self.message_port_register_in(pmt.intern('msg_in'))
        self.set_msg_handler(pmt.intern('msg_in'), self.handle_msg)

    def handle_msg(self, msg):
        text = pmt.symbol_to_string(msg)  # convert PMT to string
        print(f"RX: {text}")
        sys.stdout.flush()  # pnsure immediate print output on load, else is unreliable timing
