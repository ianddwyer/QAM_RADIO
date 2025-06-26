import sys
import os
import socket
import threading
import subprocess
import time
from pydub import AudioSegment
from PyQt5.QtWidgets import (
    QApplication, QWidget, QTabWidget, QVBoxLayout, QPushButton,
    QLabel, QFileDialog, QListWidget, QTextEdit, QLineEdit, QHBoxLayout,
    QSlider, QStyle
)
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtCore import Qt, QUrl

class UDPStreamer:
    def __init__(self, ip, port, rate):
        self.ip = ip
        self.port = port
        self.rate = rate
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        self.sock.sendto(data, (self.ip, self.port))

class AudioMessagingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio & Messaging App")
        self.setGeometry(100, 100, 800, 400)

        self.tabs = QTabWidget()
        self.audio_tab = QWidget()
        self.messaging_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.audio_tab, "Audio")
        self.tabs.addTab(self.messaging_tab, "Messaging")
        self.tabs.addTab(self.settings_tab, "Settings")

        self.layout = QVBoxLayout(self)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        self.setup_audio_tab()
        self.setup_messaging_tab()
        self.setup_settings_tab()

        self.udp_streamer = None
        self.directory = ""

    def setup_audio_tab(self):
        layout = QVBoxLayout()

        self.select_dir_btn = QPushButton("Select Audio Directory")
        self.select_dir_btn.clicked.connect(self.select_directory)
        layout.addWidget(self.select_dir_btn)

        self.file_list = QListWidget()
        self.file_list.itemClicked.connect(self.load_audio)
        layout.addWidget(self.file_list)

        self.player = QMediaPlayer(None, QMediaPlayer.StreamPlayback)

        self.slider = QSlider(Qt.Horizontal)
        self.slider.setRange(0, 0)
        self.slider.sliderMoved.connect(self.set_position)
        layout.addWidget(self.slider)

        controls = QHBoxLayout()
        self.play_btn = QPushButton()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        self.play_btn.clicked.connect(self.toggle_play)
        controls.addWidget(self.play_btn)

        self.prev_btn = QPushButton("Previous")
        self.prev_btn.clicked.connect(self.play_previous)
        controls.addWidget(self.prev_btn)

        self.next_btn = QPushButton("Next")
        self.next_btn.clicked.connect(self.play_next)
        controls.addWidget(self.next_btn)

        self.mute_btn = QPushButton("Mute")
        self.mute_btn.setCheckable(True)
        self.mute_btn.clicked.connect(self.toggle_mute)
        controls.addWidget(self.mute_btn)

        layout.addLayout(controls)
        self.audio_tab.setLayout(layout)

        self.player.positionChanged.connect(self.position_changed)
        self.player.durationChanged.connect(self.duration_changed)

    def setup_messaging_tab(self):
        layout = QVBoxLayout()
        self.message_view = QTextEdit()
        self.message_view.setReadOnly(True)
        layout.addWidget(self.message_view)

        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Type message and press Enter")
        self.message_input.returnPressed.connect(self.send_message)
        layout.addWidget(self.message_input)

        self.messaging_tab.setLayout(layout)

    def setup_settings_tab(self):
        layout = QVBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("UDP IP")
        layout.addWidget(self.ip_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("UDP Port")
        layout.addWidget(self.port_input)

        self.rate_input = QLineEdit()
        self.rate_input.setPlaceholderText("UDP Rate")
        layout.addWidget(self.rate_input)

        self.set_udp_btn = QPushButton("Set UDP Settings")
        self.set_udp_btn.clicked.connect(self.set_udp_settings)
        layout.addWidget(self.set_udp_btn)

        self.gr_file_input = QLineEdit()
        self.gr_file_input.setPlaceholderText("GNU Radio script filename")
        layout.addWidget(self.gr_file_input)

        self.run_gr_btn = QPushButton("Run GNU Radio")
        self.run_gr_btn.clicked.connect(self.run_gnuradio_script)
        layout.addWidget(self.run_gr_btn)

        self.settings_tab.setLayout(layout)

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.directory:
            self.file_list.clear()
            for filename in os.listdir(self.directory):
                if filename.endswith(".wav"):
                    self.file_list.addItem(filename)

    def load_audio(self, item):
        file_path = os.path.join(self.directory, item.text())
        self.player.setMedia(QMediaContent(QUrl.fromLocalFile(file_path)))
        self.player.play()
        self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

        if self.udp_streamer:
            threading.Thread(target=self.stream_audio_udp, args=(file_path,), daemon=True).start()

    def stream_audio_udp(self, filepath):
        try:
            audio = AudioSegment.from_file(filepath, format="wav")
            sample_rate = audio.frame_rate
            bytes_per_frame = audio.frame_width

            chunk_ms = 100
            chunk_size = int(sample_rate * (chunk_ms / 1000.0)) * bytes_per_frame

            i = 0
            while i < len(audio.raw_data):
                chunk = audio.raw_data[i:i + chunk_size]
                self.udp_streamer.send(chunk)
                i += chunk_size
                time.sleep(chunk_ms / 1000.0)
        except Exception as e:
            print("Error streaming audio to UDP:", e)

    def toggle_play(self):
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
        else:
            self.player.play()
            self.play_btn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))

    def toggle_mute(self):
        self.player.setMuted(self.mute_btn.isChecked())

    def play_previous(self):
        current_row = self.file_list.currentRow()
        if current_row > 0:
            self.file_list.setCurrentRow(current_row - 1)
            self.load_audio(self.file_list.currentItem())

    def play_next(self):
        current_row = self.file_list.currentRow()
        if current_row < self.file_list.count() - 1:
            self.file_list.setCurrentRow(current_row + 1)
            self.load_audio(self.file_list.currentItem())

    def position_changed(self, position):
        self.slider.setValue(position)

    def duration_changed(self, duration):
        self.slider.setRange(0, duration)

    def set_position(self, position):
        self.player.setPosition(position)

    def send_message(self):
        message = self.message_input.text()
        if message:
            self.message_view.append(f"You: {message}")
            if self.udp_streamer:
                self.udp_streamer.send(message.encode())
            self.message_input.clear()

    def set_udp_settings(self):
        ip = self.ip_input.text()
        port = int(self.port_input.text())
        rate = int(self.rate_input.text())
        self.udp_streamer = UDPStreamer(ip, port, rate)

    def run_gnuradio_script(self):
        script_file = self.gr_file_input.text()
        if script_file and os.path.isfile(script_file):
            subprocess.Popen([sys.executable, script_file])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AudioMessagingApp()
    window.show()
    sys.exit(app.exec_())
