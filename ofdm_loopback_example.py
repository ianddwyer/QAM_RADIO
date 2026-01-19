#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: OFDM Loopback Example
# Description: Transmit a pre-defined signal (a complex sine) as OFDM packets.
# GNU Radio version: 3.10.10.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
from gnuradio import audio
from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import uhd
import time
import satellites.hier
import sip



class ofdm_loopback_example(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "OFDM Loopback Example", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("OFDM Loopback Example")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except BaseException as exc:
            print(f"Qt GUI: Could not set Icon: {str(exc)}", file=sys.stderr)
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "ofdm_loopback_example")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.samp_rate = samp_rate = 2e6
        self.fft_len = fft_len = 32
        self.txgain = txgain = 60
        self.rxgain = rxgain = 4
        self.packet_len = packet_len = 128-1
        self.ofdm_rate = ofdm_rate = samp_rate/(fft_len+8)
        self.len_tag_key = len_tag_key = "packet_len"
        self.device_rate = device_rate = 44100
        self.centerf = centerf = 912e6
        self.access_key = access_key = '11100001010110101110100010010011'

        ##################################################
        # Blocks
        ##################################################

        self._txgain_range = qtgui.Range(0, 60, 1, 60, 8)
        self._txgain_win = qtgui.RangeWidget(self._txgain_range, self.set_txgain, "Transmit Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._txgain_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._rxgain_range = qtgui.Range(4, 40, 1, 4, 8)
        self._rxgain_win = qtgui.RangeWidget(self._rxgain_range, self.set_rxgain, "Receive Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rxgain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_source_0_0 = uhd.usrp_source(
            ",".join(("", "serial=15YWBBW")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_0_0.set_center_freq(centerf, 0)
        self.uhd_usrp_source_0_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_0_0.set_gain(rxgain, 0)
        self.uhd_usrp_sink_0_0 = uhd.usrp_sink(
            ",".join(("", "serial=UF7ENUJ")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_0_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0_0.set_center_freq(centerf, 0)
        self.uhd_usrp_sink_0_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0_0.set_gain(txgain, 0)
        self.satellites_rms_agc_1 = satellites.hier.rms_agc(alpha=0.000001, reference=0.707)
        self.satellites_rms_agc_0 = satellites.hier.rms_agc(alpha=0.000001, reference=0.707)
        self.qtgui_freq_sink_x_0 = qtgui.freq_sink_c(
            1024, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            0, #fc
            samp_rate, #bw
            'Rx Spectrum', #name
            2,
            None # parent
        )
        self.qtgui_freq_sink_x_0.set_update_time(0.10)
        self.qtgui_freq_sink_x_0.set_y_axis((-70), (-20))
        self.qtgui_freq_sink_x_0.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0.enable_autoscale(False)
        self.qtgui_freq_sink_x_0.enable_grid(False)
        self.qtgui_freq_sink_x_0.set_fft_average(1.0)
        self.qtgui_freq_sink_x_0.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0.enable_control_panel(False)
        self.qtgui_freq_sink_x_0.set_fft_window_normalized(False)



        labels = ['Rx Spectrum', '', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_win = sip.wrapinstance(self.qtgui_freq_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_freq_sink_x_0_win)
        self.mmse_resampler_xx_2_0 = filter.mmse_resampler_ff(0, (ofdm_rate/samp_rate))
        self.mmse_resampler_xx_2_0.set_max_output_buffer(int(2e6))
        self.mmse_resampler_xx_2 = filter.mmse_resampler_ff(0, (samp_rate/ofdm_rate))
        self.mmse_resampler_xx_2.set_max_output_buffer(int(2e6))
        self.digital_ofdm_tx_0 = digital.ofdm_tx(
            fft_len=fft_len,
            cp_len=(fft_len//4),
            packet_length_tag_key=len_tag_key,
            occupied_carriers=((-4,-3,-2,-1,1,2,3,4),),
            pilot_carriers=((-6,-5,5,6),),
            pilot_symbols=((-1,1,-1,1),),
            sync_word1=None,
            sync_word2=None,
            bps_header=1,
            bps_payload=2,
            rolloff=0,
            debug_log=False,
            scramble_bits=False)
        self.digital_ofdm_tx_0.set_max_output_buffer(200000)
        self.digital_ofdm_rx_0 = digital.ofdm_rx(
            fft_len=fft_len, cp_len=(fft_len//4),
            frame_length_tag_key='frame_'+"rx_len",
            packet_length_tag_key="rx_len",
            occupied_carriers=((-4,-3,-2,-1,1,2,3,4),),
            pilot_carriers=((-6,-5,5,6),),
            pilot_symbols=((-1,1,-1,1),),
            sync_word1=None,
            sync_word2=None,
            bps_header=1,
            bps_payload=2,
            debug_log=False,
            scramble_bits=False)
        self.digital_ofdm_rx_0.set_max_output_buffer(200000)
        self.blocks_wavfile_source_0 = blocks.wavfile_source("music/Not In My Arms (Calibeats Remix)  Takara.mp3", True)
        self.blocks_wavfile_source_0.set_max_output_buffer(int(2e6))
        self.blocks_tag_debug_0 = blocks.tag_debug(gr.sizeof_char*1, 'Rx Packets', "")
        self.blocks_tag_debug_0.set_display(False)
        self.blocks_stream_to_tagged_stream_0 = blocks.stream_to_tagged_stream(gr.sizeof_char, 1, packet_len, len_tag_key)
        self.blocks_probe_rate_0 = blocks.probe_rate(gr.sizeof_float*1, 500.0, 0.15, 'rate')
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff((1/127))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff(127)
        self.blocks_message_debug_0 = blocks.message_debug(True, gr.log_levels.info)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)
        self.blocks_correctiq_auto_0 = blocks.correctiq_auto(samp_rate, centerf, 1, 2)
        self.blocks_char_to_float_0 = blocks.char_to_float(1, 1)
        self.audio_sink_0 = audio.sink(int(device_rate), '', True)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_probe_rate_0, 'rate'), (self.blocks_message_debug_0, 'print'))
        self.connect((self.blocks_char_to_float_0, 0), (self.mmse_resampler_xx_2_0, 0))
        self.connect((self.blocks_correctiq_auto_0, 0), (self.digital_ofdm_rx_0, 0))
        self.connect((self.blocks_correctiq_auto_0, 0), (self.qtgui_freq_sink_x_0, 0))
        self.connect((self.blocks_float_to_char_0, 0), (self.blocks_stream_to_tagged_stream_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mmse_resampler_xx_2, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_stream_to_tagged_stream_0, 0), (self.digital_ofdm_tx_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_ofdm_rx_0, 0), (self.blocks_char_to_float_0, 0))
        self.connect((self.digital_ofdm_rx_0, 0), (self.blocks_tag_debug_0, 0))
        self.connect((self.digital_ofdm_tx_0, 0), (self.satellites_rms_agc_1, 0))
        self.connect((self.mmse_resampler_xx_2, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.mmse_resampler_xx_2_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.mmse_resampler_xx_2_0, 0), (self.blocks_probe_rate_0, 0))
        self.connect((self.satellites_rms_agc_0, 0), (self.blocks_correctiq_auto_0, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.qtgui_freq_sink_x_0, 1))
        self.connect((self.satellites_rms_agc_1, 0), (self.uhd_usrp_sink_0_0, 0))
        self.connect((self.uhd_usrp_source_0_0, 0), (self.satellites_rms_agc_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "ofdm_loopback_example")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_ofdm_rate(self.samp_rate/(self.fft_len+8))
        self.mmse_resampler_xx_2.set_resamp_ratio((self.samp_rate/self.ofdm_rate))
        self.mmse_resampler_xx_2_0.set_resamp_ratio((self.ofdm_rate/self.samp_rate))
        self.qtgui_freq_sink_x_0.set_frequency_range(0, self.samp_rate)
        self.uhd_usrp_sink_0_0.set_samp_rate(self.samp_rate)
        self.uhd_usrp_source_0_0.set_samp_rate(self.samp_rate)

    def get_fft_len(self):
        return self.fft_len

    def set_fft_len(self, fft_len):
        self.fft_len = fft_len
        self.set_ofdm_rate(self.samp_rate/(self.fft_len+8))

    def get_txgain(self):
        return self.txgain

    def set_txgain(self, txgain):
        self.txgain = txgain
        self.uhd_usrp_sink_0_0.set_gain(self.txgain, 0)

    def get_rxgain(self):
        return self.rxgain

    def set_rxgain(self, rxgain):
        self.rxgain = rxgain
        self.uhd_usrp_source_0_0.set_gain(self.rxgain, 0)

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len
        self.blocks_stream_to_tagged_stream_0.set_packet_len(self.packet_len)
        self.blocks_stream_to_tagged_stream_0.set_packet_len_pmt(self.packet_len)

    def get_ofdm_rate(self):
        return self.ofdm_rate

    def set_ofdm_rate(self, ofdm_rate):
        self.ofdm_rate = ofdm_rate
        self.mmse_resampler_xx_2.set_resamp_ratio((self.samp_rate/self.ofdm_rate))
        self.mmse_resampler_xx_2_0.set_resamp_ratio((self.ofdm_rate/self.samp_rate))

    def get_len_tag_key(self):
        return self.len_tag_key

    def set_len_tag_key(self, len_tag_key):
        self.len_tag_key = len_tag_key

    def get_device_rate(self):
        return self.device_rate

    def set_device_rate(self, device_rate):
        self.device_rate = device_rate
        self.blocks_throttle2_0.set_sample_rate(self.device_rate)
        self.blocks_throttle2_1.set_sample_rate(self.device_rate)

    def get_centerf(self):
        return self.centerf

    def set_centerf(self, centerf):
        self.centerf = centerf
        self.blocks_correctiq_auto_0.set_freq(self.centerf)
        self.uhd_usrp_sink_0_0.set_center_freq(self.centerf, 0)
        self.uhd_usrp_source_0_0.set_center_freq(self.centerf, 0)

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key




def main(top_block_cls=ofdm_loopback_example, options=None):
    if gr.enable_realtime_scheduling() != gr.RT_OK:
        gr.logger("realtime").warn("Error: failed to enable real-time scheduling.")

    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()

    tb.start()

    tb.show()

    def sig_handler(sig=None, frame=None):
        tb.stop()
        tb.wait()

        Qt.QApplication.quit()

    signal.signal(signal.SIGINT, sig_handler)
    signal.signal(signal.SIGTERM, sig_handler)

    timer = Qt.QTimer()
    timer.start(500)
    timer.timeout.connect(lambda: None)

    qapp.exec_()

if __name__ == '__main__':
    main()
