import sys
import os
import subprocess
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QFileDialog, QLineEdit, QListWidget, QMessageBox
)

from pydub import AudioSegment

LAST_DIR_FILE = "last_dir.txt"

class AudioStreamer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Audio Streamer to UDP")
        self.setGeometry(100, 100, 500, 400)
        self.layout = QVBoxLayout()
        self.sample_rate = 44100 #the value set
        self.audio_rate = 44100 #the value pulled from file
        self.port = 5006
        self.ip = "127.0.0.1"
        self.directory = os.path.join(os.getcwd(),"music")

        self.dir_button = QPushButton("Select Audio Directory")
        self.dir_button.clicked.connect(self.select_directory)
        self.layout.addWidget(self.dir_button)

        self.file_list = QListWidget()
        self.file_list.itemDoubleClicked.connect(self.stream_selected_file)
        self.layout.addWidget(self.file_list)

        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Destination IP (default 127.0.0.1)")
        self.layout.addWidget(self.ip_input)

        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("Destination Port (default 5006)")
        self.layout.addWidget(self.port_input)

        self.setLayout(self.layout)
        self.ffmpeg_process = None

        self.load_last_directory()

    def load_last_directory(self):
        try:
            if os.path.exists(LAST_DIR_FILE):
                with open(LAST_DIR_FILE, "r") as f:
                    last_dir = f.read().strip()
                    if os.path.isdir(last_dir):
                        self.populate_file_list()
        except Exception as e: print("Failed to load last directory:", e)

    def select_directory(self):
        self.directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if self.directory:
            self.populate_file_list(self.directory)
            try:
                with open(LAST_DIR_FILE, "w") as f: f.write(self.directory)
            except Exception as e: print("Failed to save last directory:", e)

    def populate_file_list(self):
        self.file_list.clear()
        for file in os.listdir(self.directory):
            audio = AudioSegment.from_file(os.path.join(self.directory, file))  # Works with .mp3 or .wav
            audio_rate = audio.frame_rate
            if (file.lower().endswith(".wav") or file.lower().endswith(".mp3")): self.file_list.addItem(str(audio_rate)+ ":" +file)

    def stream_selected_file(self):
        selected_items = self.file_list.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No File", "Please select a .wav or .mp3 file.")
            return
        
        file_path = os.path.normpath(os.path.join(self.directory, selected_items[0].text().split(":")[1]))
        audio = AudioSegment.from_file(file_path)  # Works with .mp3 or .wav
        audio_rate = audio.frame_rate
        
        if self.ip_input.text() !="": self.ip = self.ip_input.text().strip()
        if self.port_input.text()!="":self.port = self.port_input.text().strip()
        if self.ffmpeg_process: self.ffmpeg_process.kill()

        command = [
            "ffmpeg",
            "-re", #real time playback
            "-i", file_path, #file to play
            "-ac", "1", #mono for 1 and stereo for 2
            "-ar", str(audio_rate), #audio playback rate
            "-f", "f32le", #32 bit float for gnuradio
            "-packetsize","32", #in bytes (gnuradio is in bytes as well)
            f"udp://{self.ip}:{self.port}" #where to transport stream
        ]

        try: self.ffmpeg_process = subprocess.Popen(command)
        except Exception as e:  QMessageBox.critical(self, "Error Starting FFmpeg", str(e))

    def closeEvent(self, event):
        if self.ffmpeg_process: self.ffmpeg_process.kill()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    try:
        streamer = AudioStreamer()
        streamer.show()
        sys.exit(app.exec_())
    except Exception as e:
        print("Application failed to start:", e)
