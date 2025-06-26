import numpy as np
import pmt
from gnuradio import gr

class blk(gr.sync_block):
    def __init__(self):
        gr.sync_block.__init__(self,
            name="msg_phase_rotator",
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )

        self.phase = 0.0
        self.rotation = 1.0 + 0j  # complex rotator
        self.message_port_register_in(pmt.intern("phase_cmd"))
        self.set_msg_handler(pmt.intern("phase_cmd"), self.handle_msg)

    def handle_msg(self, msg):
        try:
            angle_deg = int(pmt.symbol_to_string(msg))
            self.phase = np.deg2rad(angle_deg)
            self.rotation = np.exp(1j * self.phase)
            print(f"[Phase Rotator] Set phase to {angle_deg}°")
        except Exception as e:
            print(f"[Phase Rotator] Failed to parse message: {msg}, error: {e}")

    def work(self, input_items, output_items):
        output_items[0][:] = input_items[0] * self.rotation
        return len(output_items[0])
