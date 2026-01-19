import numpy as np
from gnuradio import gr
import sys

class blk(gr.decim_block):
    def __init__(self, byte_order="little"):
        gr.decim_block.__init__(
            self,
            name="u8x4_to_stereo_f32_i16unpack",
            in_sig=[np.uint8],
            out_sig=[np.float32, np.float32],
            decim=4,
        )
        self.byte_order = str(byte_order).lower()

    def work(self, input_items, output_items):
        x = input_items[0]
        l_out = output_items[0]
        r_out = output_items[1]

        n_out = min(len(l_out), len(r_out), len(x) // 4)
        if n_out <= 0:
            return 0

        b = x[:4*n_out].reshape(n_out, 4)

        want_little = (self.byte_order != "big")
        host_little = (sys.byteorder == "little")
        if want_little != host_little:
            b = b[:, ::-1]

        u32 = b.reshape(4*n_out).view(np.uint32)

        hi = (u32 >> 16).astype(np.uint16)
        lo = (u32 & 0xFFFF).astype(np.uint16)

        li16 = hi.view(np.int16)
        ri16 = lo.view(np.int16)

        l = li16.astype(np.float32) / 32768.0
        r = ri16.astype(np.float32) / 32768.0

        l_out[:n_out] = np.clip(l, -1.0, 1.0)
        r_out[:n_out] = np.clip(r, -1.0, 1.0)
        return n_out
