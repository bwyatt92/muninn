import speech_recognition as sr
from typing import Optional, Tuple
from config.family_names import FAMILY_MEMBERS

class SpeechToTextProcessor:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True

    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
                text = self.recognizer.recognize_google(audio)
                return text.strip()

        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def process_command(self, audio_text: str) -> Tuple[str, Optional[str]]:
        text = audio_text.lower().strip()

        # Remove wake word if present (handle both "muninn" and "munin")
        if text.startswith("muninn"):
            text = text[6:].strip()
        elif text.startswith("munin"):
            text = text[5:].strip()

        if text.startswith(","):
            text = text[1:].strip()

        # Check for recording command
        if any(phrase in text for phrase in ["remember this", "record this", "save this", "remember"]):
            return "record", None

        # Check for playback commands - improved to handle possessive and descriptive phrases
        if any(phrase in text for phrase in ["play", "hear", "listen to"]):
            # Extract family member name - handle possessive forms and descriptive text
            for member in FAMILY_MEMBERS:
                member_lower = member.lower()
                # Check for exact name, possessive form (carrie's), or in context
                if (member_lower in text or
                    f"{member_lower}'s" in text or
                    f"{member_lower}s" in text):
                    return "play", member.upper()

            # If no specific member found, return general play command
            return "play", None

        # Check for stop command
        if any(phrase in text for phrase in ["stop", "enough", "cancel", "quit"]):
            return "stop", None

        # Check for list commands
        if any(phrase in text for phrase in ["list", "show", "what do you have"]):
            return "list", None

        # Check for help commands
        if any(phrase in text for phrase in ["help", "what can you do", "commands"]):
            return "help", None

        # Default: unrecognized command
        return "unknown", text

class MockSpeechToTextProcessor:
    def __init__(self):
        print("Mock Speech-to-Text processor initialized")

    def transcribe_audio_file(self, file_path: str) -> Optional[str]:
        print(f"Mock: Transcribing {file_path}")
        # Return a mock transcription
        return "This is a mock transcription of the audio file."

    def process_command(self, audio_text: str) -> Tuple[str, Optional[str]]:
        # For testing, provide some mock command processing
        text = audio_text.lower()

        if "remember" in text:
            return "record", None
        elif "play" in text and "carrie" in text:
            return "play", "CARRIE"
        elif "stop" in text:
            return "stop", None
        else:
            return "unknown", text

def get_speech_processor():
    if Settings.MOCK_MODE:
        print("Using mock speech processor (development mode)")
        return MockSpeechToTextProcessor()

    try:
        processor = SpeechToTextProcessor()
        print("Using real speech recognition")
        return processor
    except Exception as e:
        print(f"Failed to initialize speech processor: {e}")
        print("Falling back to mock processor")
        return MockSpeechToTextProcessor()