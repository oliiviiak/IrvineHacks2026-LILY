import cv2
import sounddevice as sd
from scipy.io.wavfile import write

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
if ret:
    cv2.imwrite("photo.jpg", frame)
    print("Saved photo.jpg")
cap.release()   


duration = 5  # seconds
sample_rate = 44100

print("Recording...")
audio = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1)
sd.wait()
write("recording.wav", sample_rate, audio)
print("Saved recording.wav")