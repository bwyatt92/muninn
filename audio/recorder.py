import pyaudio
import wave
import threading
import time
import numpy as np
from typing import Optional, Callable
from config.settings import Settings

class AudioRecorder:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.recording = False
        self.frames = []
        self.stream = None
        self.record_thread = None
        self.vad_callback: Optional[Callable] = None
        self.silence_start_time = None

    def start_recording(self, filename: str, vad_callback: Optional[Callable] = None):
        if self.recording:
            print("Already recording!")
            return False

        self.frames = []
        self.recording = True
        self.vad_callback = vad_callback
        self.silence_start_time = None

        try:
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=Settings.CHANNELS,
                rate=Settings.SAMPLE_RATE,
                input=True,
                frames_per_buffer=Settings.CHUNK_SIZE
            )

            self.record_thread = threading.Thread(target=self._record_audio, args=(filename,))
            self.record_thread.start()

            print(f"Started recording to {filename}")
            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.recording = False
            return False

    def stop_recording(self):
        if not self.recording:
            return

        print("Stopping recording...")
        self.recording = False

        if self.record_thread and self.record_thread.is_alive():
            self.record_thread.join()

        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None

    def _record_audio(self, filename: str):
        print("Recording thread started")

        while self.recording:
            try:
                data = self.stream.read(Settings.CHUNK_SIZE, exception_on_overflow=False)
                self.frames.append(data)

                # Voice Activity Detection
                if self.vad_callback and Settings.VAD_SILENCE_DURATION > 0:
                    audio_data = np.frombuffer(data, dtype=np.int16)
                    energy = np.sqrt(np.mean(audio_data**2))

                    if energy < Settings.VAD_ENERGY_THRESHOLD:
                        if self.silence_start_time is None:
                            self.silence_start_time = time.time()
                        elif time.time() - self.silence_start_time > Settings.VAD_SILENCE_DURATION:
                            print("Silence detected, stopping recording")
                            self.recording = False
                            break
                    else:
                        self.silence_start_time = None

            except Exception as e:
                print(f"Error during recording: {e}")
                break

        self._save_recording(filename)
        print("Recording thread finished")

    def _save_recording(self, filename: str):
        if not self.frames:
            print("No audio data to save")
            return

        try:
            with wave.open(filename, 'wb') as wf:
                wf.setnchannels(Settings.CHANNELS)
                wf.setsampwidth(self.audio.get_sample_size(pyaudio.paInt16))
                wf.setframerate(Settings.SAMPLE_RATE)
                wf.writeframes(b''.join(self.frames))

            print(f"Audio saved to {filename}")

        except Exception as e:
            print(f"Error saving recording: {e}")

    def is_recording(self) -> bool:
        return self.recording

    def cleanup(self):
        self.stop_recording()
        self.audio.terminate()

class MockAudioRecorder:
    def __init__(self):
        self.recording = False

    def start_recording(self, filename: str, vad_callback: Optional[Callable] = None):
        if self.recording:
            print("Mock: Already recording!")
            return False

        self.recording = True
        print(f"Mock: Started recording to {filename}")

        # Simulate recording for a few seconds then auto-stop
        def mock_recording():
            time.sleep(5)  # Simulate 5 seconds of recording
            self.recording = False
            # Create a dummy audio file
            try:
                with open(filename, 'wb') as f:
                    f.write(b'MOCK_AUDIO_DATA')
                print(f"Mock: Audio saved to {filename}")
            except Exception as e:
                print(f"Mock: Error saving file: {e}")

        threading.Thread(target=mock_recording).start()
        return True

    def stop_recording(self):
        if self.recording:
            print("Mock: Stopping recording...")
            self.recording = False

    def is_recording(self) -> bool:
        return self.recording

    def cleanup(self):
        self.stop_recording()

def get_audio_recorder():
    if Settings.MOCK_MODE:
        print("Using mock audio recorder (development mode)")
        return MockAudioRecorder()

    try:
        recorder = AudioRecorder()
        print("Using real audio recorder")
        return recorder
    except Exception as e:
        print(f"Failed to initialize audio recorder: {e}")
        print("Falling back to mock recorder")
        return MockAudioRecorder()