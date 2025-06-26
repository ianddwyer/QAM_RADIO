import numpy as np
import pmt
from gnuradio import gr
import time
import threading

class blk(gr.sync_block):
    def __init__(self, timeout=2.0):
        gr.sync_block.__init__(
            self,
            name="stall_phase_rotator_loop",
            in_sig=[np.uint8],
            out_sig=[np.uint8]
        )

        self.message_port_register_out(pmt.intern("phase_cmd"))

        # Parameters
        self.timeout = float(timeout)

        # State
        self.last_seen = time.time()
        self.last_sent = 0
        self.phase_index = 0
        self.last_phase_index = -1
        self.running = True
        self.lock = threading.Lock()

        # Start monitoring thread
        self._monitor_thread = threading.Thread(target=self._monitor, daemon=True)
        self._monitor_thread.start()

    def _monitor(self):
        while self.running:
            now = time.time()
            with self.lock:
                time_since_flow = now - self.last_seen
                time_since_sent = now - self.last_sent

            if time_since_flow > self.timeout and time_since_sent > self.timeout:
                with self.lock:
                    radians = (self.phase_index * np.pi / 2) % (2 * np.pi)
                    if self.phase_index != self.last_phase_index:
                        #print(f"[STALL] No input for {time_since_flow:.2f}s. Rotating: {radians:.2f} rad")
                        self.message_port_pub(pmt.intern("phase_cmd"), pmt.from_double(radians))
                        self.last_sent = now
                        self.last_phase_index = self.phase_index
                        self.phase_index = (self.phase_index + 1) % 4

            time.sleep(self.timeout)

    def work(self, input_items, output_items):
        ninput = len(input_items[0])
        if ninput > 0:
            with self.lock:
                self.last_seen = time.time()
        output_items[0] = input_items[0]
        self.consume(0, ninput)
        return len(output_items)

    def stop(self):
        self.running = False
        return super().stop()
