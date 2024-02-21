import sys
import threading
import cv2
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QPushButton, QVBoxLayout, QWidget
import audio
import pyaudio
import wave
from pydub import AudioSegment
import time
import numpy as np



class VideoPlayer(QWidget):
    def __init__(self, file_name):
        super().__init__()

        self.content_layout = QVBoxLayout(self)

        self.video_label = QLabel(self)
        self.play_button = QPushButton("Play", self)
        self.play_button.clicked.connect(self.toggle_play)

        self.content_layout.addWidget(self.video_label)
        self.content_layout.addWidget(self.play_button)
        self.file_name = file_name
        self.cap = cv2.VideoCapture(file_name)  # Thay thế bằng đường dẫn video thực tế
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        self.playing = False
        self.setLayout(self.content_layout)
        self.audio_thread = None
        self.show()

    def toggle_play(self):
        if not self.playing:
            self.audio_thread = threading.Thread(target=lambda : self.play_audio())
            self.audio_thread.start()
            self.play_button.setText("Pause")
            self.timer.start(30)  # Tần suất cập nhật khung hình, bạn có thể điều chỉnh tùy ý
        else:
            self.play_button.setText("Play")
            stop_flag = True
            self.timer.stop()
        self.playing = not self.playing

    def play_audio(self):
        video_audio = AudioSegment.from_file(self.file_name, format="mp4")
        raw_data = np.array(video_audio.get_array_of_samples(), dtype=np.int16)

        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16,
                        channels=video_audio.channels,
                        rate=video_audio.frame_rate,
                        output=True)

        chunk_size = 1024
        idx = 0

        while idx < len(raw_data) and self.playing:
            chunk = raw_data[idx:idx + chunk_size].tobytes()
            stream.write(chunk)
            idx += chunk_size

        stream.stop_stream()
        stream.close()
        p.terminate()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            height, width, channels = frame.shape
            frame = cv2.resize(frame, (400, int(height * 400 / width)))
            rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_image.shape
            bytes_per_line = ch * w
            q_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.video_label.setPixmap(pixmap)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    player = VideoPlayer()
    sys.exit(app.exec_())
