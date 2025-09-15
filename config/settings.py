import os
import platform
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    WAKE_WORD = "munin"  # Updated to match custom trained wake word

    # Audio settings
    SAMPLE_RATE = 16000
    CHUNK_SIZE = 1024
    CHANNELS = 1
    AUDIO_FORMAT = "WAV"

    # File paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    AUDIO_DIR = os.path.join(BASE_DIR, "audio_files")
    DATABASE_PATH = os.path.join(BASE_DIR, "muninn.db")

    # Hardware detection
    IS_RASPBERRY_PI = platform.machine() in ["armv7l", "aarch64"]

    # Picovoice access key
    PICOVOICE_ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")

    # Custom wake word file path
    WAKE_WORD_MODEL_PATH = os.path.join(BASE_DIR, "munin_en_raspberry-pi_v3_0_0.ppn")

    # LED settings
    LED_COUNT = 60
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 255
    LED_INVERT = False
    LED_CHANNEL = 0

    # Mock mode for development (only on non-Pi systems)
    MOCK_MODE = not IS_RASPBERRY_PI

    # Voice Activity Detection
    VAD_SILENCE_DURATION = 3.0  # seconds of silence before stopping recording
    VAD_ENERGY_THRESHOLD = 300

    @classmethod
    def ensure_directories(cls):
        os.makedirs(cls.AUDIO_DIR, exist_ok=True)