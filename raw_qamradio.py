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
import os
import sys
sys.path.append(os.environ.get('GRC_HIER_PATH', os.path.expanduser('~/.grc_gnuradio')))

from PyQt5 import QtCore
from gnuradio import blocks
from gnuradio import blocks, gr
from gnuradio import digital
from gnuradio import filter
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import network
from packetgen import packetgen  # grc-generated hier_block
from packetread import packetread  # grc-generated hier_block
import numpy as np
import raw_qamradio_epy_block_5 as epy_block_5  # embedded python block
import raw_qamradio_epy_block_6 as epy_block_6  # embedded python block
import raw_qamradio_epy_block_7 as epy_block_7  # embedded python block
import satellites.hier
import sip



class raw_qamradio(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "raw_qamradio")

        try:
            geometry = self.settings.value("geometry")
            if geometry:
                self.restoreGeometry(geometry)
        except BaseException as exc:
            print(f"Qt GUI: Could not restore geometry: {str(exc)}", file=sys.stderr)

        ##################################################
        # Variables
        ##################################################
        self.psk4 = psk4 = digital.constellation_qpsk().base()
        self.psk4.set_npwr(1)
        self.samp_rate = samp_rate = 2e6
        self.samp_per_sym = samp_per_sym = 4
        self.exbw = exbw = 1
        self.C = C = psk4
        self.symbol_rate = symbol_rate = samp_rate/samp_per_sym
        self.rxmod = rxmod = digital.generic_mod(C, True, samp_per_sym, True, exbw, False, False)
        self.packet_len = packet_len = 1024
        self.message = message = 0
        self.access_key = access_key = '11100001010110101110100010010011'
        self.umm = umm = "music/I Don't Know.wav"
        self.txgain = txgain = 60
        self.shift = shift = samp_rate/4
        self.rxgain = rxgain = 18
        self.rrc_taps = rrc_taps = firdes.root_raised_cosine(32, 32, 1.0/float(samp_per_sym), exbw, 11*samp_per_sym*packet_len)
        self.random = random = 2
        self.qam8 = qam8 = digital.constellation_calcdist(np.array([-1-1j, -1+1j, 1+1j, 1-1j, -0.67j, 0.67, 0.67j, -0.67]), [0, 1, 2, 3, 4, 5 ,6 ,7],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.qam8.set_npwr(2)
        self.qam64 = qam64 = digital.constellation_calcdist(np.array([-0.70711+-0.70711j, -0.50508+-0.70711j, -0.30304+-0.70711j, -0.10101+-0.70711j, 0.10101+-0.70711j, 0.30304+-0.70711j, 0.50508+-0.70711j, 0.70711+-0.70711j, -0.70711+-0.50508j, -0.50508+-0.50508j, -0.30304+-0.50508j, -0.10101+-0.50508j, 0.10101+-0.50508j, 0.30304+-0.50508j, 0.50508+-0.50508j, 0.70711+-0.50508j, -0.70711+-0.30304j, -0.50508+-0.30304j, -0.30304+-0.30304j, -0.10101+-0.30304j, 0.10101+-0.30304j, 0.30304+-0.30304j, 0.50508+-0.30304j, 0.70711+-0.30304j, -0.70711+-0.10101j, -0.50508+-0.10101j, -0.30304+-0.10101j, -0.10101+-0.10101j, 0.10101+-0.10101j, 0.30304+-0.10101j, 0.50508+-0.10101j, 0.70711+-0.10101j, -0.70711+0.10101j, -0.50508+0.10101j, -0.30304+0.10101j, -0.10101+0.10101j, 0.10101+0.10101j, 0.30304+0.10101j, 0.50508+0.10101j, 0.70711+0.10101j, -0.70711+0.30304j, -0.50508+0.30304j, -0.30304+0.30304j, -0.10101+0.30304j, 0.10101+0.30304j, 0.30304+0.30304j, 0.50508+0.30304j, 0.70711+0.30304j, -0.70711+0.50508j, -0.50508+0.50508j, -0.30304+0.50508j, -0.10101+0.50508j, 0.10101+0.50508j, 0.30304+0.50508j, 0.50508+0.50508j, 0.70711+0.50508j, -0.70711+0.70711j, -0.50508+0.70711j, -0.30304+0.70711j, -0.10101+0.70711j, 0.10101+0.70711j, 0.30304+0.70711j, 0.50508+0.70711j, 0.70711+0.70711j])/0.707, list(range(64)),
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.qam64.set_npwr(2)
        self.qam16 = qam16 = digital.constellation_16qam().base()
        self.qam16.set_npwr(2)
        self.psk8 = psk8 = digital.constellation_8psk().base()
        self.psk8.set_npwr(2)
        self.psk2 = psk2 = digital.constellation_calcdist(np.array([-1, 1]), [0, 1],
        4, 1, digital.constellation.NO_NORMALIZATION).base()
        self.psk2.set_npwr(2)
        self.ppm = ppm = 0.3
        self.port = port = 5005
        self.nfilt = nfilt = 512
        self.next_episode = next_episode = "music/Dr. Dre - The Next Episode (Wooli Flip).wav"
        self.music = music = 1
        self.modulated_sync_word = modulated_sync_word = digital.modulate_vector_bc(rxmod.to_basic_block(), [225, 90, 232, 147, 1, 0, 1, 0], [1])
        self.inputtype_sel = inputtype_sel = message
        self.hunter = hunter = "music/Subtronics x Flowdan - Hunter.wav"
        self.hdr_format = hdr_format = digital.header_format_default(access_key, 0)
        self.final_breath = final_breath = "music/Final Breath.wav"
        self.device_rate = device_rate = 44100
        self.centerf = centerf = 0.912e9
        self.bandwidth = bandwidth = symbol_rate*(1+exbw)
        self.aa = aa = digital.adaptive_algorithm_cma( C, 0.0005, C.arity()).base()

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
        self.satellites_rms_agc_1 = satellites.hier.rms_agc(alpha=0.00001, reference=0.9)
        self._rxgain_range = qtgui.Range(7, 40, 1, 18, 8)
        self._rxgain_win = qtgui.RangeWidget(self._rxgain_range, self.set_rxgain, "Receive Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rxgain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_1 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_BLACKMAN_hARRIS, #wintype
            centerf, #fc
            samp_rate, #bw
            "", #name
            2,
            None # parent
        )
        self.qtgui_freq_sink_x_0_1.set_update_time(0.05)
        self.qtgui_freq_sink_x_0_1.set_y_axis((-80), (-20))
        self.qtgui_freq_sink_x_0_1.set_y_label('Relative Gain', 'dB')
        self.qtgui_freq_sink_x_0_1.set_trigger_mode(qtgui.TRIG_MODE_FREE, 0.0, 0, "")
        self.qtgui_freq_sink_x_0_1.enable_autoscale(False)
        self.qtgui_freq_sink_x_0_1.enable_grid(True)
        self.qtgui_freq_sink_x_0_1.set_fft_average(0.1)
        self.qtgui_freq_sink_x_0_1.enable_axis_labels(True)
        self.qtgui_freq_sink_x_0_1.enable_control_panel(True)
        self.qtgui_freq_sink_x_0_1.set_fft_window_normalized(False)



        labels = ['RX', 'TX', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "green", "black", "cyan",
            "magenta", "yellow", "dark red", "dark green", "dark blue"]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(2):
            if len(labels[i]) == 0:
                self.qtgui_freq_sink_x_0_1.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_freq_sink_x_0_1.set_line_label(i, labels[i])
            self.qtgui_freq_sink_x_0_1.set_line_width(i, widths[i])
            self.qtgui_freq_sink_x_0_1.set_line_color(i, colors[i])
            self.qtgui_freq_sink_x_0_1.set_line_alpha(i, alphas[i])

        self._qtgui_freq_sink_x_0_1_win = sip.wrapinstance(self.qtgui_freq_sink_x_0_1.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_freq_sink_x_0_1_win, 3, 1, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.qtgui_freq_sink_x_0_1.set_max_output_buffer(int(2e6))
        self.qtgui_eye_sink_x_0 = qtgui.eye_sink_c(
            1024, #size
            samp_rate/samp_per_sym, #samp_rate
            1, #number of inputs
            None
        )
        self.qtgui_eye_sink_x_0.set_update_time(0.10)
        self.qtgui_eye_sink_x_0.set_samp_per_symbol(1)
        self.qtgui_eye_sink_x_0.set_y_axis(-1, 1)

        self.qtgui_eye_sink_x_0.set_y_label('Amplitude', "")

        self.qtgui_eye_sink_x_0.enable_tags(True)
        self.qtgui_eye_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, 0, "")
        self.qtgui_eye_sink_x_0.enable_autoscale(False)
        self.qtgui_eye_sink_x_0.enable_grid(False)
        self.qtgui_eye_sink_x_0.enable_axis_labels(True)
        self.qtgui_eye_sink_x_0.enable_control_panel(False)


        labels = ['Signal 1', 'Signal 2', 'Signal 3', 'Signal 4', 'Signal 5',
            'Signal 6', 'Signal 7', 'Signal 8', 'Signal 9', 'Signal 10']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ['blue', 'blue', 'blue', 'blue', 'blue',
            'blue', 'blue', 'blue', 'blue', 'blue']
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]
        styles = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        markers = [-1, -1, -1, -1, -1,
            -1, -1, -1, -1, -1]


        for i in range(2):
            if len(labels[i]) == 0:
                if (i % 2 == 0):
                    self.qtgui_eye_sink_x_0.set_line_label(i, "Eye [Re{{Data {0}}}]".format(round(i/2)))
                else:
                    self.qtgui_eye_sink_x_0.set_line_label(i, "Eye [Im{{Data {0}}}]".format(round((i-1)/2)))
            else:
                self.qtgui_eye_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_eye_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_eye_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_eye_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_eye_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_eye_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_eye_sink_x_0_win = sip.wrapinstance(self.qtgui_eye_sink_x_0.qwidget(), Qt.QWidget)
        self.top_layout.addWidget(self._qtgui_eye_sink_x_0_win)
        self.qtgui_const_sink_x_0 = qtgui.const_sink_c(
            (1024*C.bits_per_symbol()), #size
            "", #name
            1, #number of inputs
            None # parent
        )
        self.qtgui_const_sink_x_0.set_update_time(0.1)
        self.qtgui_const_sink_x_0.set_y_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_x_axis((-2), 2)
        self.qtgui_const_sink_x_0.set_trigger_mode(qtgui.TRIG_MODE_FREE, qtgui.TRIG_SLOPE_POS, 0.0, 0, "")
        self.qtgui_const_sink_x_0.enable_autoscale(False)
        self.qtgui_const_sink_x_0.enable_grid(True)
        self.qtgui_const_sink_x_0.enable_axis_labels(True)


        labels = ['RX', 'TX', '', '', '',
            '', '', '', '', '']
        widths = [1, 1, 1, 1, 1,
            1, 1, 1, 1, 1]
        colors = ["blue", "red", "red", "red", "red",
            "red", "red", "red", "red", "red"]
        styles = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        markers = [0, 0, 0, 0, 0,
            0, 0, 0, 0, 0]
        alphas = [1.0, 1.0, 1.0, 1.0, 1.0,
            1.0, 1.0, 1.0, 1.0, 1.0]

        for i in range(1):
            if len(labels[i]) == 0:
                self.qtgui_const_sink_x_0.set_line_label(i, "Data {0}".format(i))
            else:
                self.qtgui_const_sink_x_0.set_line_label(i, labels[i])
            self.qtgui_const_sink_x_0.set_line_width(i, widths[i])
            self.qtgui_const_sink_x_0.set_line_color(i, colors[i])
            self.qtgui_const_sink_x_0.set_line_style(i, styles[i])
            self.qtgui_const_sink_x_0.set_line_marker(i, markers[i])
            self.qtgui_const_sink_x_0.set_line_alpha(i, alphas[i])

        self._qtgui_const_sink_x_0_win = sip.wrapinstance(self.qtgui_const_sink_x_0.qwidget(), Qt.QWidget)
        self.top_grid_layout.addWidget(self._qtgui_const_sink_x_0_win, 3, 0, 1, 1)
        for r in range(3, 4):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._ppm_range = qtgui.Range(-10, 10, 0.1, 0.3, (20*10))
        self._ppm_win = qtgui.RangeWidget(self._ppm_range, self.set_ppm, "Tune PPM", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ppm_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.packetread_0 = packetread(
            access_key=access_key,
            packet_len=packet_len,
            packet_len_tagn="packet_len",
        )
        self.packetread_0.set_max_output_buffer(int(2e6))
        self.packetgen_0 = packetgen(
            access_key=access_key,
            packet_len=packet_len,
            packet_len_tagn="packet_len",
        )
        self.packetgen_0.set_max_output_buffer(int(2e6))
        self.network_udp_source_1 = network.udp_source(gr.sizeof_char, 1, 5006, 0, (packet_len*32), True, True, False)
        self.network_udp_source_1.set_max_output_buffer(int(2e6))
        self.network_udp_sink_0 = network.udp_sink(gr.sizeof_char, 1, '127.0.0.1', 5007, 0, packet_len, False)
        self.epy_block_7 = epy_block_7.blk(timeout=0.25)
        self.epy_block_6 = epy_block_6.blk(filename="snr.txt")
        self.epy_block_5 = epy_block_5.blk(fft_size=1024, avg_frames_base2=64, sample_rate=samp_rate, symbol_rate=samp_rate/samp_per_sym, excess_bw=exbw, report_interval=1)
        self.epy_block_5.set_max_output_buffer(int(2e6))
        self.digital_symbol_sync_xx_0_0 = digital.symbol_sync_cc(
            digital.TED_SIGNAL_TIMES_SLOPE_ML,
            samp_per_sym,
            0.5,
            2,
            2,
            0,
            1,
            C,
            digital.IR_PFB_MF,
            32,
            rrc_taps)
        self.digital_linear_equalizer_0 = digital.linear_equalizer(1, 1, aa, True, [ ], 'corr_est')
        self.digital_diff_decoder_bb_0_1 = digital.diff_decoder_bb(C.arity(), digital.DIFF_DIFFERENTIAL)
        self.digital_constellation_receiver_cb_0_0 = digital.constellation_receiver_cb(C, (0.0628/4), (-5000), 5000)
        self.digital_constellation_modulator_0 = digital.generic_mod(
            constellation=C,
            differential=True,
            samples_per_symbol=samp_per_sym,
            pre_diff_code=True,
            excess_bw=exbw,
            verbose=False,
            log=False,
            truncate=True)
        self.digital_constellation_modulator_0.set_max_output_buffer(int(2e6))
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(C.bits_per_symbol(), gr.GR_MSB_FIRST)
        self.blocks_probe_rate_1 = blocks.probe_rate(gr.sizeof_char*1, 2000, 0.15, '')
        self.blocks_probe_rate_1.set_max_output_buffer(int(2e6))
        self.blocks_null_sink_1_0 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_1 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_multiply_const_vxx_3 = blocks.multiply_const_cc(0.25*2*1.414)
        self.blocks_multiply_const_vxx_2 = blocks.multiply_const_cc(0.5)
        self.blocks_message_debug_1 = blocks.message_debug(True, gr.log_levels.info)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.blocks_probe_rate_1, 'rate'), (self.blocks_message_debug_1, 'print'))
        self.msg_connect((self.epy_block_5, 'snr_out'), (self.epy_block_6, 'in'))
        self.msg_connect((self.epy_block_7, 'phase_cmd'), (self.digital_constellation_receiver_cb_0_0, 'rotate_phase'))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.qtgui_freq_sink_x_0_1, 1))
        self.connect((self.blocks_multiply_const_vxx_2, 0), (self.satellites_rms_agc_1, 0))
        self.connect((self.blocks_multiply_const_vxx_3, 0), (self.digital_constellation_receiver_cb_0_0, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.blocks_probe_rate_1, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.packetread_0, 0))
        self.connect((self.digital_constellation_modulator_0, 0), (self.blocks_multiply_const_vxx_2, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 3), (self.blocks_null_sink_1_0, 2))
        self.connect((self.digital_constellation_receiver_cb_0_0, 2), (self.blocks_null_sink_1_0, 1))
        self.connect((self.digital_constellation_receiver_cb_0_0, 1), (self.blocks_null_sink_1_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 0), (self.digital_diff_decoder_bb_0_1, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 4), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_diff_decoder_bb_0_1, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.digital_linear_equalizer_0, 0), (self.blocks_multiply_const_vxx_3, 0))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self.digital_linear_equalizer_0, 0))
        self.connect((self.epy_block_7, 0), (self.blocks_null_sink_1, 0))
        self.connect((self.network_udp_source_1, 0), (self.packetgen_0, 0))
        self.connect((self.packetgen_0, 0), (self.digital_constellation_modulator_0, 0))
        self.connect((self.packetread_0, 0), (self.epy_block_7, 0))
        self.connect((self.packetread_0, 0), (self.network_udp_sink_0, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.digital_symbol_sync_xx_0_0, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.epy_block_5, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.qtgui_eye_sink_x_0, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.qtgui_freq_sink_x_0_1, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "raw_qamradio")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_psk4(self):
        return self.psk4

    def set_psk4(self, psk4):
        self.psk4 = psk4
        self.set_C(self.psk4)

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.set_shift(self.samp_rate/4)
        self.set_symbol_rate(self.samp_rate/self.samp_per_sym)
        self.epy_block_5.sample_rate = self.samp_rate
        self.epy_block_5.symbol_rate = self.samp_rate/self.samp_per_sym
        self.qtgui_eye_sink_x_0.set_samp_rate(self.samp_rate/self.samp_per_sym)
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.centerf, self.samp_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*self.samp_per_sym*self.packet_len))
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))
        self.set_symbol_rate(self.samp_rate/self.samp_per_sym)
        self.digital_symbol_sync_xx_0_0.set_sps(self.samp_per_sym)
        self.epy_block_5.symbol_rate = self.samp_rate/self.samp_per_sym
        self.qtgui_eye_sink_x_0.set_samp_rate(self.samp_rate/self.samp_per_sym)

    def get_exbw(self):
        return self.exbw

    def set_exbw(self, exbw):
        self.exbw = exbw
        self.set_bandwidth(self.symbol_rate*(1+self.exbw))
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*self.samp_per_sym*self.packet_len))
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))
        self.epy_block_5.excess_bw = self.exbw

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

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*self.samp_per_sym*self.packet_len))
        self.packetgen_0.set_packet_len(self.packet_len)
        self.packetread_0.set_packet_len(self.packet_len)

    def get_message(self):
        return self.message

    def set_message(self, message):
        self.message = message
        self.set_inputtype_sel(self.message)

    def get_access_key(self):
        return self.access_key

    def set_access_key(self, access_key):
        self.access_key = access_key
        self.set_hdr_format(digital.header_format_default(self.access_key, 0))
        self.packetgen_0.set_access_key(self.access_key)
        self.packetread_0.set_access_key(self.access_key)

    def get_umm(self):
        return self.umm

    def set_umm(self, umm):
        self.umm = umm

    def get_txgain(self):
        return self.txgain

    def set_txgain(self, txgain):
        self.txgain = txgain

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

    def get_psk2(self):
        return self.psk2

    def set_psk2(self, psk2):
        self.psk2 = psk2

    def get_ppm(self):
        return self.ppm

    def set_ppm(self, ppm):
        self.ppm = ppm

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_nfilt(self):
        return self.nfilt

    def set_nfilt(self, nfilt):
        self.nfilt = nfilt

    def get_next_episode(self):
        return self.next_episode

    def set_next_episode(self, next_episode):
        self.next_episode = next_episode

    def get_music(self):
        return self.music

    def set_music(self, music):
        self.music = music

    def get_modulated_sync_word(self):
        return self.modulated_sync_word

    def set_modulated_sync_word(self, modulated_sync_word):
        self.modulated_sync_word = modulated_sync_word

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

    def get_centerf(self):
        return self.centerf

    def set_centerf(self, centerf):
        self.centerf = centerf
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.centerf, self.samp_rate)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def get_aa(self):
        return self.aa

    def set_aa(self, aa):
        self.aa = aa




def main(top_block_cls=raw_qamradio, options=None):

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
