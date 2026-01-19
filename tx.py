#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Not titled yet
# Author: Eian
# GNU Radio version: 3.10.10.0

from PyQt5 import Qt
from gnuradio import qtgui
from PyQt5 import QtCore
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
import numpy as np



class tx(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Not titled yet", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Not titled yet")
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

        self.settings = Qt.QSettings("GNU Radio", "tx")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.psk2 = psk2 = digital.constellation_calcdist(np.array([-1, 1]), [0, 1],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.psk2.set_npwr(2)
        self.samp_rate = samp_rate = 20e6
        self.samp_per_sym = samp_per_sym = 4
        self.exbw = exbw = 1
        self.C = C = psk2
        self.symbol_rate = symbol_rate = samp_rate/samp_per_sym
        self.rxmod = rxmod = digital.generic_mod(C, True, samp_per_sym, True, exbw, False, False)
        self.music = music = 1
        self.access_key = access_key = '11100001010110101110100010010011'
        self.umm = umm = "I Don't Know.wav"
        self.txgain = txgain = 60
        self.shift = shift = samp_rate/4
        self.rxgain = rxgain = 30
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(32, 32, 1.0/float(samp_per_sym), exbw, 11*32)
        self.random = random = 2
        self.qam8 = qam8 = digital.constellation_calcdist(np.array([-1-1j, -1+1j, 1+1j, 1-1j, -0.67j, 0.67, 0.67j, -0.67]), [0, 1, 2, 3, 4, 5 ,6 ,7],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.qam8.set_npwr(2)
        self.qam64 = qam64 = digital.constellation_calcdist(np.array([-0.70711+-0.70711j, -0.50508+-0.70711j, -0.30304+-0.70711j, -0.10101+-0.70711j, 0.10101+-0.70711j, 0.30304+-0.70711j, 0.50508+-0.70711j, 0.70711+-0.70711j, -0.70711+-0.50508j, -0.50508+-0.50508j, -0.30304+-0.50508j, -0.10101+-0.50508j, 0.10101+-0.50508j, 0.30304+-0.50508j, 0.50508+-0.50508j, 0.70711+-0.50508j, -0.70711+-0.30304j, -0.50508+-0.30304j, -0.30304+-0.30304j, -0.10101+-0.30304j, 0.10101+-0.30304j, 0.30304+-0.30304j, 0.50508+-0.30304j, 0.70711+-0.30304j, -0.70711+-0.10101j, -0.50508+-0.10101j, -0.30304+-0.10101j, -0.10101+-0.10101j, 0.10101+-0.10101j, 0.30304+-0.10101j, 0.50508+-0.10101j, 0.70711+-0.10101j, -0.70711+0.10101j, -0.50508+0.10101j, -0.30304+0.10101j, -0.10101+0.10101j, 0.10101+0.10101j, 0.30304+0.10101j, 0.50508+0.10101j, 0.70711+0.10101j, -0.70711+0.30304j, -0.50508+0.30304j, -0.30304+0.30304j, -0.10101+0.30304j, 0.10101+0.30304j, 0.30304+0.30304j, 0.50508+0.30304j, 0.70711+0.30304j, -0.70711+0.50508j, -0.50508+0.50508j, -0.30304+0.50508j, -0.10101+0.50508j, 0.10101+0.50508j, 0.30304+0.50508j, 0.50508+0.50508j, 0.70711+0.50508j, -0.70711+0.70711j, -0.50508+0.70711j, -0.30304+0.70711j, -0.10101+0.70711j, 0.10101+0.70711j, 0.30304+0.70711j, 0.50508+0.70711j, 0.70711+0.70711j])/0.70711, list(range(64)),
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.qam64.set_npwr(2)
        self.qam16 = qam16 = digital.constellation_16qam().base()
        self.qam16.set_npwr(2)
        self.psk8 = psk8 = digital.constellation_8psk().base()
        self.psk8.set_npwr(2)
        self.psk4 = psk4 = digital.constellation_calcdist(np.array([-4-4j, -4+4j, 4+4j, 4-4j])/4, [0, 1, 2, 3],
        4, 1, digital.constellation.AMPLITUDE_NORMALIZATION).base()
        self.psk4.set_npwr(2)
        self.ppm = ppm = 0.3
        self.port = port = 5005
        self.packet_len = packet_len = 1024
        self.next_episode = next_episode = "Dr. Dre - The Next Episode (Wooli Flip).wav"
        self.modulated_sync_word = modulated_sync_word = digital.modulate_vector_bc(rxmod.to_basic_block(), [225, 90, 232, 147, 1, 0, 1, 0], [1])
        self.message = message = 0
        self.inputtype_sel = inputtype_sel = music
        self.hunter = hunter = "Subtronics x Flowdan - Hunter.wav"
        self.hdr_format = hdr_format = digital.header_format_default(access_key, 0)
        self.final_breath = final_breath = "Final+Breath.wav"
        self.device_rate = device_rate = 44100
        self.centerf = centerf = 0.912e9
        self.bandwidth = bandwidth = symbol_rate*(1+exbw)
        self.aa = aa = digital.adaptive_algorithm_cma( C, 0.0001, C.arity()).base()

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
        self.uhd_usrp_sink_0 = uhd.usrp_sink(
            ",".join(("", "serial=UF7ENUJ")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
            "",
        )
        self.uhd_usrp_sink_0.set_samp_rate(samp_rate)
        self.uhd_usrp_sink_0.set_time_unknown_pps(uhd.time_spec(0))

        self.uhd_usrp_sink_0.set_center_freq(centerf, 0)
        self.uhd_usrp_sink_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_sink_0.set_gain(txgain, 0)
        self._rxgain_range = qtgui.Range(7, 40, 1, 30, 8)
        self._rxgain_win = qtgui.RangeWidget(self._rxgain_range, self.set_rxgain, "Receive Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rxgain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._ppm_range = qtgui.Range(-10, 10, 0.1, 0.3, (20*10))
        self._ppm_win = qtgui.RangeWidget(self._ppm_range, self.set_ppm, "Tune PPM", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ppm_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.mmse_resampler_xx_2 = filter.mmse_resampler_ff(0, (device_rate/ (samp_rate/samp_per_sym/8*C.bits_per_symbol())))
        self.mmse_resampler_xx_2.set_max_output_buffer(int(2e6))
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=C,
            differential=True,
            samples_per_symbol=samp_per_sym,
            pre_diff_code=True,
            excess_bw=exbw,
            verbose=False,
            log=False,
            truncate=False)
        self.digital_constellation_modulator_0.set_max_output_buffer(int(2e6))
        self.blocks_wavfile_source_0 = blocks.wavfile_source("music/Not In My Arms (Calibeats Remix)  Takara.mp3", True)
        self.blocks_wavfile_source_0.set_max_output_buffer(int(2e6))
        self.blocks_probe_rate_1 = blocks.probe_rate(gr.sizeof_float*1, 2000, 0.15, '')
        self.blocks_probe_rate_1.set_max_output_buffer(int(2e6))
        self.blocks_multiply_const_xx_0 = blocks.multiply_const_cc(0.5, 1)
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_ff((127*0.5))
        self.blocks_message_debug_1 = blocks.message_debug(True, gr.log_levels.info)
        self.blocks_float_to_char_0 = blocks.float_to_char(1, 1)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_probe_rate_1, 'rate'), (self.blocks_message_debug_1, 'print'))
        self.connect((self.blocks_float_to_char_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.mmse_resampler_xx_2, 0))
        self.connect((self.blocks_multiply_const_xx_0, 0), (self.uhd_usrp_sink_0, 0))
        self.connect((self.blocks_wavfile_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_multiply_const_xx_0, 0))
        self.connect((self.mmse_resampler_xx_2, 0), (self.blocks_float_to_char_0, 0))
        self.connect((self.mmse_resampler_xx_2, 0), (self.blocks_probe_rate_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "tx")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_psk2(self):
        return self.psk2

    def set_psk2(self, psk2):
        self.psk2 = psk2
        self.set_C(self.psk2)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_shift(self.samp_rate/4)
        self.set_symbol_rate(self.samp_rate/self.samp_per_sym)
        self.mmse_resampler_xx_2.set_resamp_ratio((self.device_rate/ (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol())))
        self.uhd_usrp_sink_0.set_samp_rate(self.samp_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*32))
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))
        self.set_symbol_rate(self.samp_rate/self.samp_per_sym)
        self.mmse_resampler_xx_2.set_resamp_ratio((self.device_rate/ (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol())))

    def get_exbw(self):
        return self.exbw

    def set_exbw(self, exbw):
        self.exbw = exbw
        self.set_bandwidth(self.symbol_rate*(1+self.exbw))
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*32))
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))

    def get_C(self):
        return self.C

    def set_C(self, C):
        self.C = C
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))

    def get_symbol_rate(self):
        return self.symbol_rate

    def set_symbol_rate(self, symbol_rate):
        self.symbol_rate = symbol_rate
        self.set_bandwidth(self.symbol_rate*(1+self.exbw))

    def get_rxmod(self):
        return self.rxmod

    def set_rxmod(self, rxmod):
        self.rxmod = rxmod

    def get_music(self):
        return self.music

    def set_music(self, music):
        self.music = music
        self.set_inputtype_sel(self.music)

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key
        self.set_hdr_format(digital.header_format_default(self.access_key, 0))

    def get_umm(self):
        return self.umm

    def set_umm(self, umm):
        self.umm = umm

    def get_txgain(self):
        return self.txgain

    def set_txgain(self, txgain):
        self.txgain = txgain
        self.uhd_usrp_sink_0.set_gain(self.txgain, 0)

    def get_shift(self):
        return self.shift

    def set_shift(self, shift):
        self.shift = shift

    def get_rxgain(self):
        return self.rxgain

    def set_rxgain(self, rxgain):
        self.rxgain = rxgain

    def get_rrc_taps(self):
        return self.rrc_taps

    def set_rrc_taps(self, rrc_taps):
        self.rrc_taps = rrc_taps

    def get_random(self):
        return self.random

    def set_random(self, random):
        self.random = random

    def get_qam8(self):
        return self.qam8

    def set_qam8(self, qam8):
        self.qam8 = qam8

    def get_qam64(self):
        return self.qam64

    def set_qam64(self, qam64):
        self.qam64 = qam64

    def get_qam16(self):
        return self.qam16

    def set_qam16(self, qam16):
        self.qam16 = qam16

    def get_psk8(self):
        return self.psk8

    def set_psk8(self, psk8):
        self.psk8 = psk8

    def get_psk4(self):
        return self.psk4

    def set_psk4(self, psk4):
        self.psk4 = psk4

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len

    def get_next_episode(self):
        return self.next_episode

    def set_next_episode(self, next_episode):
        self.next_episode = next_episode

    def get_modulated_sync_word(self):
        return self.modulated_sync_word

    def set_modulated_sync_word(self, modulated_sync_word):
        self.modulated_sync_word = modulated_sync_word

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message

    def get_inputtype_sel(self):
        return self.inputtype_sel

    def set_inputtype_sel(self, inputtype_sel):
        self.inputtype_sel = inputtype_sel

    def get_hunter(self):
        return self.hunter

    def set_hunter(self, hunter):
        self.hunter = hunter

    def get_hdr_format(self):
        return self.hdr_format

    def set_hdr_format(self, hdr_format):
        self.hdr_format = hdr_format

    def get_final_breath(self):
        return self.final_breath

    def set_final_breath(self, final_breath):
        self.final_breath = final_breath

    def get_device_rate(self):
        return self.device_rate

    def set_device_rate(self, device_rate):
        self.device_rate = device_rate
        self.blocks_throttle2_0_0.set_sample_rate(self.device_rate)
        self.mmse_resampler_xx_2.set_resamp_ratio((self.device_rate/ (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol())))

    def get_centerf(self):
        return self.centerf

    def set_centerf(self, centerf):
        self.centerf = centerf
        self.uhd_usrp_sink_0.set_center_freq(self.centerf, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def get_aa(self):
        return self.aa

    def set_aa(self, aa):
        self.aa = aa




def main(top_block_cls=tx, options=None):

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
