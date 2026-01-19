import numpy as np
from gnuradio import gr
import sys

class blk(gr.decim_block):
    def __init__(self, byte_order="little"):
        gr.decim_block.__init__(
            self,
            name="u8x4_to_f32",
            in_sig=[np.uint8],
            out_sig=[np.float32],
            decim=4,
        )
        self.byte_order = str(byte_order).lower()

    def work(self, input_items, output_items):
        x = input_items[0]
        out = output_items[0]

        n_out = min(len(out), len(x) // 4)
        if n_out <= 0:
            return 0

        b = x[:4*n_out].reshape(n_out, 4)

        want_little = (self.byte_order != "big")
        host_little = (sys.byteorder == "little")
        if want_little != host_little:
            b = b[:, ::-1]

        out[:n_out] = b.reshape(4*n_out).view(np.float32)
        return n_out
