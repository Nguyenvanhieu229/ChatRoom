import pyaudio
from pydub import AudioSegment
import numpy as np
import threading

video_audio = AudioSegment.from_file("test_medium.mp4", format="mp4")
raw_data = np.array(video_audio.get_array_of_samples(), dtype=np.int16)

p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=video_audio.channels,
                rate=video_audio.frame_rate,
                output=True)

chunk_size = 1024
idx = 0

while idx < len(raw_data):
    chunk = raw_data[idx:idx + chunk_size].tobytes()
    stream.write(chunk)
    idx += chunk_size

stream.stop_stream()
stream.close()
p.terminate()