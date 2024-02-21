import sys
import time
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QApplication
from moviepy.editor import VideoFileClip
import threading
import pyaudio
import wave
from pydub import AudioSegment
import time

def extract_audio(input_video, output_audio):
    # Load video clip
    video_clip = VideoFileClip(input_video)

    # Extract audio
    audio_clip = video_clip.audio

    # Save audio as MP3
    audio_clip.write_audiofile(output_audio)

    video_clip.close()
    audio_clip.close()

    return output_audio

class AudioPlayer(QWidget):

    def __init__(self, fr, file_name):
        super().__init__()
        self.content_layout = QVBoxLayout(self)
        self.playing = True
        self.file_name = file_name
        self.label = QLabel(f"{fr} đã gửi một audio: ", self)
        self.play_button = QPushButton("Play", self)

        self.play_button.clicked.connect(lambda : self.toggle_play(file_name))
        self.audio_thread = None
        self.content_layout.addWidget(self.label)
        self.content_layout.addWidget(self.play_button)

        self.setLayout(self.content_layout)
        self.show()

    def toggle_play(self, file_name):
        if not self.playing:
            self.audio_thread = threading.Thread(target=lambda : self.play_audio())
            self.audio_thread.start()
            self.play_button.setText("Pause")
            # Tần suất cập nhật khung hình, bạn có thể điều chỉnh tùy ý
        else:
            self.play_button.setText("Play")
        self.playing = not self.playing

    def play_audio(self):
        sound = AudioSegment.from_mp3(self.file_name)
        raw_data = sound.raw_data
        sample_width = sound.sample_width
        channels = sound.channels
        frame_rate = sound.frame_rate

        p = pyaudio.PyAudio()
        stream = p.open(format=p.get_format_from_width(sample_width),
                        channels=channels,
                        rate=frame_rate,
                        output=True)

        chunk_size = 1024
        idx = 0

        while idx < len(raw_data) and self.playing:
            chunk = raw_data[idx:idx + chunk_size]
            stream.write(chunk)
            idx += chunk_size

        stream.stop_stream()
        stream.close()
        p.terminate()


