#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: srsRAN_multi_UE
# GNU Radio version: 3.10.1.1

from packaging.version import Version as StrictVersion

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print("Warning: failed to XInitThreads()")

from PyQt5 import Qt
from PyQt5.QtCore import QObject, pyqtSlot
from gnuradio import blocks
from gnuradio import channels
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore
import math



from gnuradio import qtgui

class multi_ue_scenario(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "srsRAN_multi_UE", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("srsRAN_multi_UE")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
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

        self.settings = Qt.QSettings("GNU Radio", "multi_ue_scenario")

        try:
            if StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
                self.restoreGeometry(self.settings.value("geometry").toByteArray())
            else:
                self.restoreGeometry(self.settings.value("geometry"))
        except:
            pass

        ##################################################
        # Variables
        ##################################################
        self.zmq_timeout = zmq_timeout = 500
        self.zmq_hwm = zmq_hwm = -1
        self.t = t = 0
        self.speed2 = speed2 = 10
        self.speed1 = speed1 = 10
        self.slow_down_ratio = slow_down_ratio = 1
        self.samp_rate = samp_rate = 11520000
        self.frequence = frequence = 3685000000
        self.c = c = 300000000
        self.X2 = X2 = -1300
        self.X1 = X1 = 1500

        ##################################################
        # Blocks
        ##################################################
        self._t_range = Range(0, 3000, 1, 0, 200)
        self._t_win = RangeWidget(self._t_range, self.set_t, "'t'", "counter_slider", int, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._t_win)
        # Create the options list
        self._speed2_options = [10, 30, 60, 70]
        # Create the labels list
        self._speed2_labels = ['10', '30', '60', '70']
        # Create the combo box
        self._speed2_tool_bar = Qt.QToolBar(self)
        self._speed2_tool_bar.addWidget(Qt.QLabel("'speed2'" + ": "))
        self._speed2_combo_box = Qt.QComboBox()
        self._speed2_tool_bar.addWidget(self._speed2_combo_box)
        for _label in self._speed2_labels: self._speed2_combo_box.addItem(_label)
        self._speed2_callback = lambda i: Qt.QMetaObject.invokeMethod(self._speed2_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._speed2_options.index(i)))
        self._speed2_callback(self.speed2)
        self._speed2_combo_box.currentIndexChanged.connect(
            lambda i: self.set_speed2(self._speed2_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._speed2_tool_bar)
        # Create the options list
        self._speed1_options = [10, 30, 60, 70]
        # Create the labels list
        self._speed1_labels = ['10', '30', '60', '70']
        # Create the combo box
        self._speed1_tool_bar = Qt.QToolBar(self)
        self._speed1_tool_bar.addWidget(Qt.QLabel("'speed1'" + ": "))
        self._speed1_combo_box = Qt.QComboBox()
        self._speed1_tool_bar.addWidget(self._speed1_combo_box)
        for _label in self._speed1_labels: self._speed1_combo_box.addItem(_label)
        self._speed1_callback = lambda i: Qt.QMetaObject.invokeMethod(self._speed1_combo_box, "setCurrentIndex", Qt.Q_ARG("int", self._speed1_options.index(i)))
        self._speed1_callback(self.speed1)
        self._speed1_combo_box.currentIndexChanged.connect(
            lambda i: self.set_speed1(self._speed1_options[i]))
        # Create the radio buttons
        self.top_layout.addWidget(self._speed1_tool_bar)
        self.zeromq_req_source_1_0 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:4201', zmq_timeout, False, zmq_hwm)
        self.zeromq_req_source_1 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2101', zmq_timeout, False, zmq_hwm)
        self.zeromq_req_source_0 = zeromq.req_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2000', zmq_timeout, False, zmq_hwm)
        self.zeromq_rep_sink_0_1 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2001', zmq_timeout, False, zmq_hwm)
        self.zeromq_rep_sink_0_0 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:4200', zmq_timeout, False, zmq_hwm)
        self.zeromq_rep_sink_0 = zeromq.rep_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2100', zmq_timeout, False, zmq_hwm)
        self._slow_down_ratio_range = Range(1, 32, 1, 1, 200)
        self._slow_down_ratio_win = RangeWidget(self._slow_down_ratio_range, self.set_slow_down_ratio, "Time Slow Down Ratio", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._slow_down_ratio_win)
        self.channels_dynamic_channel_model_2 = channels.dynamic_channel_model(
            samp_rate,
            0.01,
            1e3,
            0.01,
            1e3,
            8,
            (speed2/3.6)*(36.85/3),
            False,
            4.0,
            [0,0.00000031,0.00000071,0.00000109,0.00000173,0.00000251],
            [0,-1,-9,-10,-15,-20],
            6,
            0,
            0)
        self.channels_dynamic_channel_model_1 = channels.dynamic_channel_model(
            samp_rate,
            0.01,
            1e3,
            0.01,
            1e3,
            8,
            (speed1/3.6)*(36.85/3),
            False,
            4.0,
            [0,0.00000031,0.00000071,0.00000109,0.00000173,0.00000251],
            [0,-1,-9,-10,-15,-20],
            6,
            0,
            0)
        self.channels_dynamic_channel_model_0_0 = channels.dynamic_channel_model(
            samp_rate,
            0.01,
            1e3,
            0.01,
            1e3,
            8,
            (speed2/3.6)*(36.85/3),
            False,
            4.0,
            [0,0.00000031,0.00000071,0.00000109,0.00000173,0.00000251],
            [0,-1,-9,-10,-15,-20],
            6,
            0,
            0)
        self.channels_dynamic_channel_model_0 = channels.dynamic_channel_model(
            samp_rate,
            0.01,
            1e3,
            0.01,
            1e3,
            8,
            (speed1/3.6)*(36.85/3),
            False,
            4.0,
            [0,0.00000031,0.00000071,0.00000109,0.00000173,0.00000251],
            [0,-1,-9,-10,-15,-20],
            6,
            0,
            0)
        self.blocks_throttle_0_1 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_throttle_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        self.blocks_multiply_const_vxx_0_2 = blocks.multiply_const_cc(10**(-math.log10(abs(X2-speed2*t/3.6))-math.log10(frequence)-math.log10(4*math.pi/c)))
        self.blocks_multiply_const_vxx_0_1 = blocks.multiply_const_cc(10**(-math.log10(abs(X1+t*speed1/3.6))-math.log10(frequence)-math.log10(4*math.pi/c)))
        self.blocks_multiply_const_vxx_0_0 = blocks.multiply_const_cc(10**(-math.log10(abs(X2-speed2*t/3.6))-math.log10(frequence)-math.log10(4*math.pi/c)))
        self.blocks_multiply_const_vxx_0 = blocks.multiply_const_cc(10**(-math.log10(abs(X1+t*speed1/3.6))-math.log10(frequence)-math.log10(4*math.pi/c)))
        self.blocks_add_xx_0 = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.blocks_add_xx_0, 0), (self.zeromq_rep_sink_0_1, 0))
        self.connect((self.blocks_multiply_const_vxx_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_0, 0), (self.blocks_throttle_0_0_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_1, 0), (self.blocks_throttle_0, 0))
        self.connect((self.blocks_multiply_const_vxx_0_2, 0), (self.blocks_throttle_0_1, 0))
        self.connect((self.blocks_throttle_0, 0), (self.channels_dynamic_channel_model_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.channels_dynamic_channel_model_1, 0))
        self.connect((self.blocks_throttle_0_0_0, 0), (self.channels_dynamic_channel_model_2, 0))
        self.connect((self.blocks_throttle_0_1, 0), (self.channels_dynamic_channel_model_0_0, 0))
        self.connect((self.channels_dynamic_channel_model_0, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.channels_dynamic_channel_model_0_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.channels_dynamic_channel_model_1, 0), (self.zeromq_rep_sink_0, 0))
        self.connect((self.channels_dynamic_channel_model_2, 0), (self.zeromq_rep_sink_0_0, 0))
        self.connect((self.zeromq_req_source_0, 0), (self.blocks_multiply_const_vxx_0, 0))
        self.connect((self.zeromq_req_source_0, 0), (self.blocks_multiply_const_vxx_0_0, 0))
        self.connect((self.zeromq_req_source_1, 0), (self.blocks_multiply_const_vxx_0_1, 0))
        self.connect((self.zeromq_req_source_1_0, 0), (self.blocks_multiply_const_vxx_0_2, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "multi_ue_scenario")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_zmq_timeout(self):
        return self.zmq_timeout

    def set_zmq_timeout(self, zmq_timeout):
        self.zmq_timeout = zmq_timeout

    def get_zmq_hwm(self):
        return self.zmq_hwm

    def set_zmq_hwm(self, zmq_hwm):
        self.zmq_hwm = zmq_hwm

    def get_t(self):
        return self.t

    def set_t(self, t):
        self.t = t
        self.blocks_multiply_const_vxx_0.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_0.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_2.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))

    def get_speed2(self):
        return self.speed2

    def set_speed2(self, speed2):
        self.speed2 = speed2
        self._speed2_callback(self.speed2)
        self.blocks_multiply_const_vxx_0_0.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_2.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.channels_dynamic_channel_model_0_0.set_doppler_freq((self.speed2/3.6)*(36.85/3))
        self.channels_dynamic_channel_model_2.set_doppler_freq((self.speed2/3.6)*(36.85/3))

    def get_speed1(self):
        return self.speed1

    def set_speed1(self, speed1):
        self.speed1 = speed1
        self._speed1_callback(self.speed1)
        self.blocks_multiply_const_vxx_0.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.channels_dynamic_channel_model_0.set_doppler_freq((self.speed1/3.6)*(36.85/3))
        self.channels_dynamic_channel_model_1.set_doppler_freq((self.speed1/3.6)*(36.85/3))

    def get_slow_down_ratio(self):
        return self.slow_down_ratio

    def set_slow_down_ratio(self, slow_down_ratio):
        self.slow_down_ratio = slow_down_ratio

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_0_0.set_sample_rate(self.samp_rate)
        self.blocks_throttle_0_1.set_sample_rate(self.samp_rate)
        self.channels_dynamic_channel_model_0.set_samp_rate(self.samp_rate)
        self.channels_dynamic_channel_model_0_0.set_samp_rate(self.samp_rate)
        self.channels_dynamic_channel_model_1.set_samp_rate(self.samp_rate)
        self.channels_dynamic_channel_model_2.set_samp_rate(self.samp_rate)

    def get_frequence(self):
        return self.frequence

    def set_frequence(self, frequence):
        self.frequence = frequence
        self.blocks_multiply_const_vxx_0.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_0.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_2.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))

    def get_c(self):
        return self.c

    def set_c(self, c):
        self.c = c
        self.blocks_multiply_const_vxx_0.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_0.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_2.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))

    def get_X2(self):
        return self.X2

    def set_X2(self, X2):
        self.X2 = X2
        self.blocks_multiply_const_vxx_0_0.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_2.set_k(10**(-math.log10(abs(self.X2-self.speed2*self.t/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))

    def get_X1(self):
        return self.X1

    def set_X1(self, X1):
        self.X1 = X1
        self.blocks_multiply_const_vxx_0.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))
        self.blocks_multiply_const_vxx_0_1.set_k(10**(-math.log10(abs(self.X1+self.t*self.speed1/3.6))-math.log10(self.frequence)-math.log10(4*math.pi/self.c)))




def main(top_block_cls=multi_ue_scenario, options=None):

    if StrictVersion("4.5.0") <= StrictVersion(Qt.qVersion()) < StrictVersion("5.0.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
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
