#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#
# SPDX-License-Identifier: GPL-3.0
#
# GNU Radio Python Flow Graph
# Title: Handover Simulation (gNB1 <-> gNB2)
# Author: Expert srsRAN
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

from gnuradio import blocks
from gnuradio import gr
from gnuradio.filter import firdes
from gnuradio.fft import window
import sys
import signal
from PyQt5 import Qt
from argparse import ArgumentParser
from gnuradio.eng_arg import eng_float, intx
from gnuradio import eng_notation
from gnuradio import zeromq
from gnuradio.qtgui import Range, RangeWidget
from PyQt5 import QtCore



from gnuradio import qtgui

class handover_test(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Handover Simulation (gNB1 <-> gNB2)", catch_exceptions=True)
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Handover Simulation (gNB1 <-> gNB2)")
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

        self.settings = Qt.QSettings("GNU Radio", "handover_test")

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
        self.sample_rate = sample_rate = 11520000
        self.ho_gn2 = ho_gn2 = 0
        self.ho_gn1 = ho_gn1 = 1
        self.gain_gn2 = gain_gn2 = 0
        self.gain_gn1 = gain_gn1 = 1

        ##################################################
        # Blocks
        ##################################################
        self._gain_gn2_range = Range(0, 1, 0.01, 0, 200)
        self._gain_gn2_win = RangeWidget(self._gain_gn2_range, self.set_gain_gn2, "'gain_gn2'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_gn2_win)
        self._gain_gn1_range = Range(0, 1, 0.01, 1, 200)
        self._gain_gn1_win = RangeWidget(self._gain_gn1_range, self.set_gain_gn1, "'gain_gn1'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._gain_gn1_win)
        self.ue_tx_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:4101', zmq_timeout, False, -1, '')
        self.ue_rx_sink = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:4100', zmq_timeout, False, -1, '')
        self.throttle_ul = blocks.throttle(gr.sizeof_gr_complex*1, sample_rate,True)
        self.throttle_dl = blocks.throttle(gr.sizeof_gr_complex*1, sample_rate,True)
        self.multiply_gnb2_0 = blocks.multiply_const_cc(gain_gn2)
        self.multiply_gnb2 = blocks.multiply_const_cc(gain_gn2)
        self.multiply_gnb1_0 = blocks.multiply_const_cc(gain_gn1)
        self.multiply_gnb1 = blocks.multiply_const_cc(gain_gn1)
        self._ho_gn2_range = Range(0, 1, 0.01, 0, 200)
        self._ho_gn2_win = RangeWidget(self._ho_gn2_range, self.set_ho_gn2, "'ho_gn2'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ho_gn2_win)
        self._ho_gn1_range = Range(0, 1, 0.01, 1, 200)
        self._ho_gn1_win = RangeWidget(self._ho_gn1_range, self.set_ho_gn1, "'ho_gn1'", "counter_slider", float, QtCore.Qt.Horizontal)
        self.top_layout.addWidget(self._ho_gn1_win)
        self.gnb2_tx_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:3000', zmq_timeout, False, -1, '')
        self.gnb2_rx_sink = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:3001', zmq_timeout, False, -1, '')
        self.gnb1_tx_source = zeromq.sub_source(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2000', zmq_timeout, False, -1, '')
        self.gnb1_rx_sink = zeromq.pub_sink(gr.sizeof_gr_complex, 1, 'tcp://127.0.0.1:2001', zmq_timeout, False, -1, '')
        self.add_signals = blocks.add_vcc(1)


        ##################################################
        # Connections
        ##################################################
        self.connect((self.add_signals, 0), (self.throttle_dl, 0))
        self.connect((self.gnb1_tx_source, 0), (self.multiply_gnb1, 0))
        self.connect((self.gnb2_tx_source, 0), (self.multiply_gnb2, 0))
        self.connect((self.multiply_gnb1, 0), (self.add_signals, 0))
        self.connect((self.multiply_gnb1_0, 0), (self.gnb2_rx_sink, 0))
        self.connect((self.multiply_gnb2, 0), (self.add_signals, 1))
        self.connect((self.multiply_gnb2_0, 0), (self.gnb1_rx_sink, 0))
        self.connect((self.throttle_dl, 0), (self.ue_rx_sink, 0))
        self.connect((self.throttle_ul, 0), (self.multiply_gnb1_0, 0))
        self.connect((self.throttle_ul, 0), (self.multiply_gnb2_0, 0))
        self.connect((self.ue_tx_source, 0), (self.throttle_ul, 0))


    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "handover_test")
        self.settings.setValue("geometry", self.saveGeometry())
        self.stop()
        self.wait()

        event.accept()

    def get_zmq_timeout(self):
        return self.zmq_timeout

    def set_zmq_timeout(self, zmq_timeout):
        self.zmq_timeout = zmq_timeout

    def get_sample_rate(self):
        return self.sample_rate

    def set_sample_rate(self, sample_rate):
        self.sample_rate = sample_rate
        self.throttle_dl.set_sample_rate(self.sample_rate)
        self.throttle_ul.set_sample_rate(self.sample_rate)

    def get_ho_gn2(self):
        return self.ho_gn2

    def set_ho_gn2(self, ho_gn2):
        self.ho_gn2 = ho_gn2

    def get_ho_gn1(self):
        return self.ho_gn1

    def set_ho_gn1(self, ho_gn1):
        self.ho_gn1 = ho_gn1

    def get_gain_gn2(self):
        return self.gain_gn2

    def set_gain_gn2(self, gain_gn2):
        self.gain_gn2 = gain_gn2
        self.multiply_gnb2.set_k(self.gain_gn2)
        self.multiply_gnb2_0.set_k(self.gain_gn2)

    def get_gain_gn1(self):
        return self.gain_gn1

    def set_gain_gn1(self, gain_gn1):
        self.gain_gn1 = gain_gn1
        self.multiply_gnb1.set_k(self.gain_gn1)
        self.multiply_gnb1_0.set_k(self.gain_gn1)




def main(top_block_cls=handover_test, options=None):

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
