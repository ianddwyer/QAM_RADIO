# -*- coding: utf-8 -*-
"""
Created on Tue Apr 15 02:21:22 2025

@author: Eian
"""

import numpy
from gnuradio import gr

class tag_counter_block(gr.sync_block):
    def __init__(self,rxflag=0):
        gr.sync_block.__init__(
            self, 
            name="Tag Counter",
            in_sig=[numpy.float32], 
            out_sig=[numpy.float32])
        self.tag_count = 0
        self.rxflag = 0

    def work(self, input_items, output_items):
        
        tags = self.get_tags_in_window(0, 0, len(input_items[0]))# Get tags in the current work call
        self.tag_count += len(tags)*self.rxflag# Count the tags
        output_items[0][:] = self.tag_count # Pass data through
        return len(output_items[0]) #return length of output for tag ref
