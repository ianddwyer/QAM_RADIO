import numpy as np
from gnuradio import gr
import sys

class blk(gr.interp_block):
    def __init__(self, byte_order="little"):
        gr.interp_block.__init__(
            self,
            name="f32_to_u8x4",
            in_sig=[np.float32],
            out_sig=[np.uint8],
            interp=4,
        )
        self.byte_order = str(byte_order).lower()

    def work(self, input_items, output_items):
        x = input_items[0]
        out = output_items[0]

        n_in = min(len(x), len(out) // 4)
        if n_in <= 0:
            return 0

        b = x[:n_in].view(np.uint8).reshape(n_in, 4)

        want_little = (self.byte_order != "big")
        host_little = (sys.byteorder == "little")
        if want_little != host_little:
            b = b[:, ::-1]

        out[:4*n_in] = b.reshape(4*n_in)
        return 4 * n_in
