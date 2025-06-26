from gnuradio import gr
import pmt

class PMTByteArrayToString(gr.basic_block):
    def __init__(self):
        gr.basic_block.__init__(
            self,
            name="Bytes to String",
            in_sig=None, out_sig=None
        )

        # Register input and output message ports
        self.message_port_register_in(pmt.intern("in"))
        self.message_port_register_out(pmt.intern("out"))
        self.set_msg_handler(pmt.intern("in"), self.handle_msg)

    def handle_msg(self, msg):

        # ensure the input is a PMT byte vector, not a PDU
        if not pmt.is_u8vector(msg): return

        # convert PMT byte vector to a Python byte array
        byte_array = bytearray(pmt.u8vector_elements(msg))

        # convert bytes to string (UTF-8 decoding), use try for safety in live streaming
        try:string_message = byte_array.decode("utf-8")
        except UnicodeDecodeError: string_message = byte_array.decode("ISO-8859-1")  # Fallback use ISO format for compatibility

        # publish the string as a PMT symbol (message)
        self.message_port_pub(pmt.intern("out"), pmt.intern(string_message))
