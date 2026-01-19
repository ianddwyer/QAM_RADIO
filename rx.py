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
from gnuradio import audio
from gnuradio import blocks
import math
from gnuradio import digital
from gnuradio import filter
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import uhd
import time
from packetread import packetread  # grc-generated hier_block
import numpy as np
import rx_epy_block_0 as epy_block_0  # embedded python block
import rx_epy_block_1 as epy_block_1  # embedded python block
import rx_epy_block_3 as epy_block_3  # embedded python block
import rx_epy_block_4 as epy_block_4  # embedded python block
import rx_epy_block_7 as epy_block_7  # embedded python block
import satellites.hier
import sip
import threading



class rx(gr.top_block, Qt.QWidget):

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

        self.settings = Qt.QSettings("GNU Radio", "rx")

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
        self.samp_rate = samp_rate = 4e6
        self.samp_per_sym = samp_per_sym = 4
        self.exbw = exbw = 1
        self.C = C = psk2
        self.symbol_rate = symbol_rate = samp_rate/samp_per_sym
        self.success = success = 0
        self.rxmod = rxmod = digital.generic_mod(C, True, samp_per_sym, True, exbw, False, False)
        self.music = music = 1
        self.access_key = access_key = '11100001010110101110100010010011'
        self.variable_qtgui_label_2 = variable_qtgui_label_2 = success
        self.umm = umm = "I Don't Know.wav"
        self.txgain = txgain = 60
        self.shift = shift = samp_rate/4
        self.rxstartflag = rxstartflag = 0
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

        self._rxgain_range = qtgui.Range(7, 40, 1, 30, 8)
        self._rxgain_win = qtgui.RangeWidget(self._rxgain_range, self.set_rxgain, "Receive Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._rxgain_win, 0, 1, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.rx_start_flag = blocks.probe_signal_f()
        self._ppm_range = qtgui.Range(-10, 10, 0.1, 0.3, (20*10))
        self._ppm_win = qtgui.RangeWidget(self._ppm_range, self.set_ppm, "Tune PPM", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._ppm_win, 1, 1, 1, 1)
        for r in range(1, 2):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self._variable_qtgui_label_2_tool_bar = Qt.QToolBar(self)

        if None:
            self._variable_qtgui_label_2_formatter = None
        else:
            self._variable_qtgui_label_2_formatter = lambda x: eng_notation.num_to_str(x)

        self._variable_qtgui_label_2_tool_bar.addWidget(Qt.QLabel("Success Packets: "))
        self._variable_qtgui_label_2_label = Qt.QLabel(str(self._variable_qtgui_label_2_formatter(self.variable_qtgui_label_2)))
        self._variable_qtgui_label_2_tool_bar.addWidget(self._variable_qtgui_label_2_label)
        self.top_grid_layout.addWidget(self._variable_qtgui_label_2_tool_bar, 0, 0, 1, 1)
        for r in range(0, 1):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(0, 1):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.uhd_usrp_source_0 = uhd.usrp_source(
            ",".join(("", "serial=15YWBBW")),
            uhd.stream_args(
                cpu_format="fc32",
                args='',
                channels=list(range(0,1)),
            ),
        )
        self.uhd_usrp_source_0.set_samp_rate(samp_rate)
        self.uhd_usrp_source_0.set_time_now(uhd.time_spec(time.time()), uhd.ALL_MBOARDS)

        self.uhd_usrp_source_0.set_center_freq(centerf+shift, 0)
        self.uhd_usrp_source_0.set_antenna("TX/RX", 0)
        self.uhd_usrp_source_0.set_gain(rxgain, 0)
        self._txgain_range = qtgui.Range(0, 60, 1, 60, 8)
        self._txgain_win = qtgui.RangeWidget(self._txgain_range, self.set_txgain, "Transmit Gain", "counter", float, QtCore.Qt.Horizontal)
        self.top_grid_layout.addWidget(self._txgain_win, 2, 1, 1, 1)
        for r in range(2, 3):
            self.top_grid_layout.setRowStretch(r, 1)
        for c in range(1, 2):
            self.top_grid_layout.setColumnStretch(c, 1)
        self.successpackets = blocks.probe_signal_f()
        def _success_probe():
          while True:

            val = self.successpackets.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_success,val))
              except AttributeError:
                self.set_success(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (1000))
        _success_thread = threading.Thread(target=_success_probe)
        _success_thread.daemon = True
        _success_thread.start()
        self.satellites_rms_agc_1_0 = satellites.hier.rms_agc(alpha=0.00001, reference=0.925)
        self.satellites_rms_agc_1 = satellites.hier.rms_agc(alpha=0.000001, reference=0.95)
        def _rxstartflag_probe():
          while True:

            val = self.rx_start_flag.level()
            try:
              try:
                self.doc.add_next_tick_callback(functools.partial(self.set_rxstartflag,val))
              except AttributeError:
                self.set_rxstartflag(val)
            except AttributeError:
              pass
            time.sleep(1.0 / (1000))
        _rxstartflag_thread = threading.Thread(target=_rxstartflag_probe)
        _rxstartflag_thread.daemon = True
        _rxstartflag_thread.start()
        self.qtgui_freq_sink_x_0_1 = qtgui.freq_sink_c(
            4096, #size
            window.WIN_RECTANGULAR, #wintype
            centerf, #fc
            samp_rate, #bw
            "", #name
            1,
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

        for i in range(1):
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
        self.packetread_0 = packetread(
            access_key=access_key,
            packet_len=packet_len,
            packet_len_tagn="packet_len",
        )
        self.packetread_0.set_max_output_buffer(int(2e6))
        self.mmse_resampler_xx_2_0 = filter.mmse_resampler_ff(0, ( (samp_rate/samp_per_sym/8*C.bits_per_symbol()*packet_len/(packet_len+12))/device_rate))
        self.mmse_resampler_xx_2_0.set_max_output_buffer(int(2e6))
        self.epy_block_7 = epy_block_7.blk(timeout=0.2)
        self.epy_block_4 = epy_block_4.print_message_block()
        self.epy_block_3 = epy_block_3.PMTByteArrayToString()
        self.epy_block_1 = epy_block_1.DropByteToMessage(dropvalue=0)
        self.epy_block_0 = epy_block_0.tag_counter_block()
        self.epy_block_0.set_max_output_buffer(int(2e6))
        self.digital_symbol_sync_xx_0_0 = digital.symbol_sync_cc(
            digital.TED_SIGNAL_TIMES_SLOPE_ML,
            samp_per_sym,
            (samp_rate/centerf*abs(ppm)/100),
            2,
            0.0001,
            0,
            1,
            C.base(),
            digital.IR_PFB_MF,
            32,
            rrc_taps)
        self.digital_linear_equalizer_0 = digital.linear_equalizer(1, 1, aa, True, [ ], 'corr_est')
        self.digital_diff_decoder_bb_0_1 = digital.diff_decoder_bb(C.arity(), digital.DIFF_DIFFERENTIAL)
        self.digital_constellation_receiver_cb_0_0 = digital.constellation_receiver_cb(C, (0.0628/8), (-0.7), 0.7)
        self.blocks_unpacked_to_packed_xx_0 = blocks.unpacked_to_packed_bb(C.bits_per_symbol(), gr.GR_MSB_FIRST)
        self.blocks_threshold_ff_0 = blocks.threshold_ff(0, 1, 0)
        self.blocks_selector_0 = blocks.selector(gr.sizeof_char*1,0,inputtype_sel)
        self.blocks_selector_0.set_enabled(True)
        self.blocks_selector_0.set_max_output_buffer(int(2e6))
        self.blocks_null_sink_1_1 = blocks.null_sink(gr.sizeof_float*1)
        self.blocks_null_sink_1_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_null_sink_0 = blocks.null_sink(gr.sizeof_char*1)
        self.blocks_multiply_const_vxx_1 = blocks.multiply_const_ff((1/127))
        self.blocks_freqshift_cc_0 = blocks.rotator_cc(2.0*math.pi*shift/samp_rate)
        self.blocks_file_sink_0_0_0 = blocks.file_sink(gr.sizeof_float*1, 'successpktcount.bin', False)
        self.blocks_file_sink_0_0_0.set_unbuffered(False)
        self.blocks_correctiq_0 = blocks.correctiq()
        self.blocks_correctiq_0.set_max_output_buffer(int(2e6))
        self.blocks_char_to_float_7 = blocks.char_to_float(1, 1)
        self.blocks_char_to_float_0_0 = blocks.char_to_float(1, 1)
        self.audio_sink_0 = audio.sink(int(device_rate), '', False)


        ##################################################
        # Connections
        ##################################################
        self.msg_connect((self.epy_block_1, 'out'), (self.epy_block_3, 'in'))
        self.msg_connect((self.epy_block_3, 'out'), (self.epy_block_4, 'msg_in'))
        self.msg_connect((self.epy_block_7, 'phase_cmd'), (self.digital_constellation_receiver_cb_0_0, 'rotate_phase'))
        self.connect((self.blocks_char_to_float_0_0, 0), (self.mmse_resampler_xx_2_0, 0))
        self.connect((self.blocks_char_to_float_7, 0), (self.epy_block_0, 0))
        self.connect((self.blocks_correctiq_0, 0), (self.blocks_freqshift_cc_0, 0))
        self.connect((self.blocks_freqshift_cc_0, 0), (self.satellites_rms_agc_1, 0))
        self.connect((self.blocks_multiply_const_vxx_1, 0), (self.audio_sink_0, 0))
        self.connect((self.blocks_selector_0, 1), (self.blocks_char_to_float_0_0, 0))
        self.connect((self.blocks_selector_0, 2), (self.blocks_null_sink_0, 0))
        self.connect((self.blocks_selector_0, 0), (self.epy_block_1, 0))
        self.connect((self.blocks_threshold_ff_0, 0), (self.rx_start_flag, 0))
        self.connect((self.blocks_unpacked_to_packed_xx_0, 0), (self.packetread_0, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 2), (self.blocks_null_sink_1_1, 1))
        self.connect((self.digital_constellation_receiver_cb_0_0, 1), (self.blocks_null_sink_1_1, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 3), (self.blocks_null_sink_1_1, 2))
        self.connect((self.digital_constellation_receiver_cb_0_0, 0), (self.digital_diff_decoder_bb_0_1, 0))
        self.connect((self.digital_constellation_receiver_cb_0_0, 4), (self.qtgui_const_sink_x_0, 0))
        self.connect((self.digital_diff_decoder_bb_0_1, 0), (self.blocks_unpacked_to_packed_xx_0, 0))
        self.connect((self.digital_linear_equalizer_0, 0), (self.satellites_rms_agc_1_0, 0))
        self.connect((self.digital_symbol_sync_xx_0_0, 0), (self.digital_constellation_receiver_cb_0_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_file_sink_0_0_0, 0))
        self.connect((self.epy_block_0, 0), (self.blocks_threshold_ff_0, 0))
        self.connect((self.epy_block_0, 0), (self.successpackets, 0))
        self.connect((self.epy_block_7, 0), (self.blocks_null_sink_1_0, 0))
        self.connect((self.mmse_resampler_xx_2_0, 0), (self.blocks_multiply_const_vxx_1, 0))
        self.connect((self.packetread_0, 0), (self.blocks_char_to_float_7, 0))
        self.connect((self.packetread_0, 0), (self.blocks_selector_0, 0))
        self.connect((self.packetread_0, 0), (self.epy_block_7, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.digital_linear_equalizer_0, 0))
        self.connect((self.satellites_rms_agc_1, 0), (self.qtgui_freq_sink_x_0_1, 0))
        self.connect((self.satellites_rms_agc_1_0, 0), (self.digital_symbol_sync_xx_0_0, 0))
        self.connect((self.uhd_usrp_source_0, 0), (self.blocks_correctiq_0, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "rx")
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
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*self.shift/self.samp_rate)
        self.digital_symbol_sync_xx_0_0.set_loop_bandwidth((self.samp_rate/self.centerf*abs(self.ppm)/100))
        self.mmse_resampler_xx_2_0.set_resamp_ratio(( (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol()*self.packet_len/(self.packet_len+12))/self.device_rate))
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.centerf, self.samp_rate)
        self.uhd_usrp_source_0.set_samp_rate(self.samp_rate)

    def get_samp_per_sym(self):
        return self.samp_per_sym

    def set_samp_per_sym(self, samp_per_sym):
        self.samp_per_sym = samp_per_sym
        self.set_rrc_taps(firdes.root_raised_cosine(32, 32, 1.0/float(self.samp_per_sym), self.exbw, 11*32))
        self.set_rxmod(digital.generic_mod(self.C, True, self.samp_per_sym, True, self.exbw, False, False))
        self.set_symbol_rate(self.samp_rate/self.samp_per_sym)
        self.digital_symbol_sync_xx_0_0.set_sps(self.samp_per_sym)
        self.mmse_resampler_xx_2_0.set_resamp_ratio(( (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol()*self.packet_len/(self.packet_len+12))/self.device_rate))

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

    def get_success(self):
        return self.success

    def set_success(self, success):
        self.success = success
        self.set_variable_qtgui_label_2(self.success)

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
        self.packetread_0.set_access_key(self.access_key)

    def get_variable_qtgui_label_2(self):
        return self.variable_qtgui_label_2

    def set_variable_qtgui_label_2(self, variable_qtgui_label_2):
        self.variable_qtgui_label_2 = variable_qtgui_label_2
        Qt.QMetaObject.invokeMethod(self._variable_qtgui_label_2_label, "setText", Qt.Q_ARG("QString", str(self._variable_qtgui_label_2_formatter(self.variable_qtgui_label_2))))

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
        self.blocks_freqshift_cc_0.set_phase_inc(2.0*math.pi*self.shift/self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.centerf+self.shift, 0)

    def get_rxstartflag(self):
        return self.rxstartflag

    def set_rxstartflag(self, rxstartflag):
        self.rxstartflag = rxstartflag

    def get_rxgain(self):
        return self.rxgain

    def set_rxgain(self, rxgain):
        self.rxgain = rxgain
        self.uhd_usrp_source_0.set_gain(self.rxgain, 0)

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
        self.digital_symbol_sync_xx_0_0.set_loop_bandwidth((self.samp_rate/self.centerf*abs(self.ppm)/100))

    def get_port(self):
        return self.port

    def set_port(self, port):
        self.port = port

    def get_packet_len(self):
        return self.packet_len

    def set_packet_len(self, packet_len):
        self.packet_len = packet_len
        self.mmse_resampler_xx_2_0.set_resamp_ratio(( (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol()*self.packet_len/(self.packet_len+12))/self.device_rate))
        self.packetread_0.set_packet_len(self.packet_len)

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
        self.blocks_selector_0.set_output_index(self.inputtype_sel)

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
        self.blocks_throttle2_0.set_sample_rate(self.device_rate)
        self.mmse_resampler_xx_2_0.set_resamp_ratio(( (self.samp_rate/self.samp_per_sym/8*C.bits_per_symbol()*self.packet_len/(self.packet_len+12))/self.device_rate))

    def get_centerf(self):
        return self.centerf

    def set_centerf(self, centerf):
        self.centerf = centerf
        self.digital_symbol_sync_xx_0_0.set_loop_bandwidth((self.samp_rate/self.centerf*abs(self.ppm)/100))
        self.qtgui_freq_sink_x_0_1.set_frequency_range(self.centerf, self.samp_rate)
        self.uhd_usrp_source_0.set_center_freq(self.centerf+self.shift, 0)

    def get_bandwidth(self):
        return self.bandwidth

    def set_bandwidth(self, bandwidth):
        self.bandwidth = bandwidth

    def get_aa(self):
        return self.aa

    def set_aa(self, aa):
        self.aa = aa




def main(top_block_cls=rx, options=None):

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
