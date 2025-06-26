import pmt
from gnuradio import gr
from datetime import datetime

class blk(gr.basic_block):
    def __init__(self, filename="output_log.txt"):
        gr.basic_block.__init__(self,
            name="PDU to Hex Log File",
            in_sig=None,
            out_sig=None)

        self.filename = filename
        self.message_port_register_in(pmt.intern("in"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)
        with open(self.filename, "w") as f:
            f.write("-")
    def handle_msg(self, msg):
        if not pmt.is_pair(msg):
            return

        meta = pmt.car(msg)
        data = pmt.cdr(msg)

        # Convert metadata to string
        meta_str = ""
        if pmt.is_dict(meta):
            keys = pmt.dict_keys(meta)
            for i in range(pmt.length(keys)):
                key = pmt.symbol_to_string(pmt.nth(i, keys))
                val = pmt.to_python(pmt.dict_ref(meta, pmt.intern(key), pmt.PMT_NIL))
                meta_str += f"{key}={val}; "

        # Convert data to hex (for u8vector)
        if pmt.is_u8vector(data):
            byte_array = bytearray(pmt.u8vector_elements(data))
            data_str = byte_array.hex(" ")  # space-separated hex bytes
        elif pmt.is_f32vector(data):
            data_list = pmt.f32vector_elements(data)
            data_str = " ".join(f"{x:.6f}" for x in data_list)
        else:
            data_str = str(pmt.to_python(data))

        # Timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        with open(self.filename, "a") as f:
            f.write(f"[time: {str(timestamp)}] meta: {str(meta_str)}| snr: {str(data_str)}\n")
