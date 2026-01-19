import numpy as np
from gnuradio import gr
import sys

class blk(gr.interp_block):
    def __init__(self, byte_order="little"):
        gr.interp_block.__init__(
            self,
            name="stereo_f32_to_u8x4_i16pack",
            in_sig=[np.float32, np.float32],
            out_sig=[np.uint8],
            interp=4,
        )
        self.byte_order = str(byte_order).lower()

    def work(self, input_items, output_items):
        l = input_items[0]
        r = input_items[1]
        out = output_items[0]

        n_in = min(len(l), len(r), len(out) // 4)
        if n_in <= 0:
            return 0

        # float in about [-1, 1) -> int16
        lq = np.clip(l[:n_in], -1.0, 1.0 - (1.0 / 32768.0))
        rq = np.clip(r[:n_in], -1.0, 1.0 - (1.0 / 32768.0))
        li16 = np.rint(lq * 32768.0).astype(np.int16)
        ri16 = np.rint(rq * 32768.0).astype(np.int16)

        # pack [L hi16][R lo16] into uint32
        lu16 = li16.view(np.uint16).astype(np.uint32)
        ru16 = ri16.view(np.uint16).astype(np.uint32)
        u32 = (lu16 << 16) | ru16

        b = u32.view(np.uint8).reshape(n_in, 4)

        want_little = (self.byte_order != "big")
        host_little = (sys.byteorder == "little")
        if want_little != host_little:
            b = b[:, ::-1]

        out[:4*n_in] = b.reshape(4*n_in)
        return 4 * n_in
