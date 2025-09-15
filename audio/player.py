import pygame
import threading
import time
from typing import Optional, Callable
from config.settings import Settings

class AudioPlayer:
    def __init__(self):
        try:
            pygame.mixer.init(frequency=Settings.SAMPLE_RATE, size=-16, channels=Settings.CHANNELS, buffer=512)
            self.initialized = True
            print("Audio player initialized with pygame")
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
            self.initialized = False

        self.is_playing = False
        self.current_file = None
        self.play_thread = None

    def play_file(self, file_path: str, completion_callback: Optional[Callable] = None) -> bool:
        if not self.initialized:
            print("Audio player not initialized")
            return False

        if self.is_playing:
            print("Already playing audio")
            return False

        if not file_path or not file_path.endswith(('.wav', '.mp3', '.ogg')):
            print(f"Unsupported audio format: {file_path}")
            return False

        try:
            self.current_file = file_path
            self.is_playing = True

            # Start playback in a separate thread
            self.play_thread = threading.Thread(
                target=self._play_audio_thread,
                args=(file_path, completion_callback)
            )
            self.play_thread.start()

            print(f"Started playing: {file_path}")
            return True

        except Exception as e:
            print(f"Error starting playback: {e}")
            self.is_playing = False
            return False

    def _play_audio_thread(self, file_path: str, completion_callback: Optional[Callable]):
        try:
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy() and self.is_playing:
                time.sleep(0.1)

        except Exception as e:
            print(f"Error during playback: {e}")

        finally:
            self.is_playing = False
            self.current_file = None

            if completion_callback:
                try:
                    completion_callback()
                except Exception as e:
                    print(f"Error in completion callback: {e}")

            print("Playback finished")

    def stop_playback(self):
        if not self.is_playing:
            return

        print("Stopping playback...")
        self.is_playing = False

        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"Error stopping playback: {e}")

        if self.play_thread and self.play_thread.is_alive():
            self.play_thread.join(timeout=2.0)

    def is_playing_audio(self) -> bool:
        return self.is_playing

    def get_current_file(self) -> Optional[str]:
        return self.current_file if self.is_playing else None

    def set_volume(self, volume: float):
        try:
            # Volume should be between 0.0 and 1.0
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
        except Exception as e:
            print(f"Error setting volume: {e}")

    def cleanup(self):
        self.stop_playback()
        try:
            pygame.mixer.quit()
        except Exception:
            pass

class MockAudioPlayer:
    def __init__(self):
        self.is_playing = False
        self.current_file = None
        print("Mock audio player initialized")

    def play_file(self, file_path: str, completion_callback: Optional[Callable] = None) -> bool:
        if self.is_playing:
            print("Mock: Already playing audio")
            return False

        self.current_file = file_path
        self.is_playing = True
        print(f"Mock: Playing {file_path}")

        # Simulate playback
        def mock_playback():
            time.sleep(3)  # Simulate 3 seconds of playback
            self.is_playing = False
            self.current_file = None
            print("Mock: Playback finished")

            if completion_callback:
                try:
                    completion_callback()
                except Exception as e:
                    print(f"Mock: Error in completion callback: {e}")

        threading.Thread(target=mock_playback).start()
        return True

    def stop_playback(self):
        if self.is_playing:
            print("Mock: Stopping playback...")
            self.is_playing = False
            self.current_file = None

    def is_playing_audio(self) -> bool:
        return self.is_playing

    def get_current_file(self) -> Optional[str]:
        return self.current_file

    def set_volume(self, volume: float):
        print(f"Mock: Setting volume to {volume}")

    def cleanup(self):
        self.stop_playback()

def get_audio_player():
    if Settings.MOCK_MODE:
        print("Using mock audio player (development mode)")
        return MockAudioPlayer()

    try:
        player = AudioPlayer()
        if player.initialized:
            print("Using real audio player")
            return player
        else:
            print("Audio player failed to initialize, using mock")
            return MockAudioPlayer()
    except Exception as e:
        print(f"Failed to initialize audio player: {e}")
        print("Falling back to mock player")
        return MockAudioPlayer()