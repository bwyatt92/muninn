import threading
import time
from typing import Callable, Optional
from config.settings import Settings

try:
    import pvporcupine
    PORCUPINE_AVAILABLE = True
except ImportError:
    PORCUPINE_AVAILABLE = False
    print("Porcupine not available, using mock wake word detection")

class WakeWordDetector:
    def __init__(self, wake_word_callback: Callable):
        self.wake_word_callback = wake_word_callback
        self.listening = False
        self.detection_thread = None
        self.porcupine = None

        if PORCUPINE_AVAILABLE and Settings.PICOVOICE_ACCESS_KEY:
            try:
                # Check if custom wake word model exists
                import os
                if os.path.exists(Settings.WAKE_WORD_MODEL_PATH):
                    # Use custom trained model
                    self.porcupine = pvporcupine.create(
                        keyword_paths=[Settings.WAKE_WORD_MODEL_PATH],
                        access_key=Settings.PICOVOICE_ACCESS_KEY
                    )
                    print(f"Porcupine initialized with custom wake word model: {Settings.WAKE_WORD}")
                    print(f"Model file: {Settings.WAKE_WORD_MODEL_PATH}")
                else:
                    # Fall back to built-in keywords
                    self.porcupine = pvporcupine.create(
                        keywords=[Settings.WAKE_WORD],
                        access_key=Settings.PICOVOICE_ACCESS_KEY
                    )
                    print(f"Porcupine initialized with built-in wake word: {Settings.WAKE_WORD}")
                    print(f"Custom model not found at: {Settings.WAKE_WORD_MODEL_PATH}")
            except Exception as e:
                print(f"Error initializing Porcupine: {e}")
                print("Check your PICOVOICE_ACCESS_KEY in .env file")
                print("Or verify your custom wake word model file")
                self.porcupine = None
        elif not Settings.PICOVOICE_ACCESS_KEY:
            print("No PICOVOICE_ACCESS_KEY found in .env file")
            self.porcupine = None

    def start_listening(self):
        if self.listening:
            print("Already listening for wake word")
            return

        self.listening = True

        if self.porcupine:
            self.detection_thread = threading.Thread(target=self._porcupine_detection_loop)
        else:
            self.detection_thread = threading.Thread(target=self._mock_detection_loop)

        self.detection_thread.start()
        print("Started listening for wake word")

    def stop_listening(self):
        if not self.listening:
            return

        print("Stopping wake word detection...")
        self.listening = False

        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join()

    def _porcupine_detection_loop(self):
        import pyaudio

        audio = pyaudio.PyAudio()
        stream = None

        try:
            stream = audio.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )

            print("Porcupine wake word detection active")

            while self.listening:
                try:
                    pcm = stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                    pcm = [int(x) for x in pcm]

                    keyword_index = self.porcupine.process(pcm)
                    if keyword_index >= 0:
                        print(f"Wake word detected: {Settings.WAKE_WORD}")
                        self.wake_word_callback()

                except Exception as e:
                    if self.listening:  # Only log if we're still supposed to be listening
                        print(f"Error in wake word detection: {e}")

        except Exception as e:
            print(f"Error setting up wake word detection: {e}")

        finally:
            if stream:
                stream.close()
            audio.terminate()

    def _mock_detection_loop(self):
        print("Mock wake word detection active - press Enter to simulate wake word")

        while self.listening:
            try:
                # In mock mode, simulate wake word detection every 10 seconds
                # In a real implementation, you might want to listen for keyboard input
                time.sleep(10)
                if self.listening:
                    print(f"Mock: Wake word '{Settings.WAKE_WORD}' detected")
                    self.wake_word_callback()

            except Exception as e:
                if self.listening:
                    print(f"Error in mock wake word detection: {e}")

    def cleanup(self):
        self.stop_listening()
        if self.porcupine:
            self.porcupine.delete()

class KeyboardWakeWordDetector:
    """Alternative wake word detector that uses keyboard input for testing"""

    def __init__(self, wake_word_callback: Callable):
        self.wake_word_callback = wake_word_callback
        self.listening = False
        self.detection_thread = None

    def start_listening(self):
        if self.listening:
            return

        self.listening = True
        self.detection_thread = threading.Thread(target=self._keyboard_detection_loop)
        self.detection_thread.start()
        print("Keyboard wake word detection active - type 'muninn' and press Enter")

    def stop_listening(self):
        self.listening = False
        if self.detection_thread and self.detection_thread.is_alive():
            self.detection_thread.join()

    def _keyboard_detection_loop(self):
        while self.listening:
            try:
                user_input = input().strip().lower()
                if user_input == Settings.WAKE_WORD and self.listening:
                    print("Wake word detected via keyboard!")
                    self.wake_word_callback()
            except (EOFError, KeyboardInterrupt):
                break
            except Exception as e:
                print(f"Error in keyboard detection: {e}")

    def cleanup(self):
        self.stop_listening()

def get_wake_word_detector(callback: Callable, use_keyboard: bool = False):
    if use_keyboard:
        return KeyboardWakeWordDetector(callback)
    else:
        return WakeWordDetector(callback)