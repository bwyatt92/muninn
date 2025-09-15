#!/usr/bin/env python3

import os
import sys
import time
import signal
import threading
from typing import Optional

# Add project root to path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from config.settings import Settings
from config.family_names import FAMILY_MEMBERS
from state.machine import StateMachine, MuninnState
from storage.database import DatabaseManager
from storage.file_manager import FileManager
from led.controller import LEDController
from audio.wake_word import get_wake_word_detector
from audio.recorder import get_audio_recorder
from audio.player import get_audio_player
from audio.speech_to_text import get_speech_processor

class MuninnVoiceAssistant:
    def __init__(self):
        print("Initializing Muninn Voice Assistant...")

        # Core components
        self.state_machine = StateMachine()
        self.database = DatabaseManager()
        self.file_manager = FileManager()
        self.led_controller = LEDController()
        self.speech_processor = get_speech_processor()

        # Audio components
        self.wake_word_detector = get_wake_word_detector(self.on_wake_word_detected)
        self.audio_recorder = get_audio_recorder()
        self.audio_player = get_audio_player()

        # State tracking
        self.current_recording_member: Optional[str] = None
        self.current_recording_file: Optional[str] = None
        self.running = False

        # Setup state machine callbacks
        self._setup_state_callbacks()

        print("Muninn initialized successfully!")
        self._print_startup_info()

    def _setup_state_callbacks(self):
        # State entry callbacks
        self.state_machine.register_state_callback(MuninnState.SLEEPING, self._on_sleeping)
        self.state_machine.register_state_callback(MuninnState.LISTENING, self._on_listening)
        self.state_machine.register_state_callback(MuninnState.RECORDING, self._on_recording)
        self.state_machine.register_state_callback(MuninnState.PLAYING, self._on_playing)
        self.state_machine.register_state_callback(MuninnState.PROCESSING, self._on_processing)

        # Transition callbacks
        self.state_machine.register_transition_callback(
            MuninnState.RECORDING, MuninnState.PROCESSING, self._on_recording_finished
        )

    def _print_startup_info(self):
        print(f"\n{'='*50}")
        print("🐦 MUNINN VOICE ASSISTANT")
        print(f"{'='*50}")
        print(f"Wake word: '{Settings.WAKE_WORD}'")
        print(f"Family members: {', '.join(FAMILY_MEMBERS)}")
        print(f"Audio directory: {Settings.AUDIO_DIR}")
        print(f"Database: {Settings.DATABASE_PATH}")

        if Settings.MOCK_MODE:
            print("🎭 Mode: DEVELOPMENT (mock audio)")
            print("   Running on non-Pi hardware")
        else:
            print("🎤 Mode: PRODUCTION")
            print("   Raspberry Pi with real hardware")
            if Settings.PICOVOICE_ACCESS_KEY:
                print("   ✓ Picovoice wake word detection enabled")
            else:
                print("   ⚠️  No Picovoice key - wake word disabled")

        print(f"{'='*50}\n")

    def start(self):
        print("Starting Muninn...")
        self.running = True

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Start the state machine
        self.state_machine.start()

        # Start wake word detection
        self.wake_word_detector.start_listening()

        print("Muninn is ready! Listening for wake word...")

        # Main loop
        try:
            while self.running:
                time.sleep(0.1)
        except KeyboardInterrupt:
            print("\nReceived interrupt signal")

        self.shutdown()

    def shutdown(self):
        print("Shutting down Muninn...")
        self.running = False

        # Stop all components
        self.wake_word_detector.stop_listening()
        self.audio_recorder.stop_recording()
        self.audio_player.stop_playback()
        self.led_controller.stop_animation()
        self.state_machine.stop()

        # Cleanup
        self.wake_word_detector.cleanup()
        self.audio_recorder.cleanup()
        self.audio_player.cleanup()

        print("Muninn shutdown complete")

    def _signal_handler(self, signum, frame):
        print(f"\nReceived signal {signum}")
        self.running = False

    # State callbacks
    def _on_sleeping(self, context: dict):
        print("State: Sleeping - waiting for wake word")
        self.led_controller.set_idle_mode()

    def _on_listening(self, context: dict):
        print("State: Listening for command")
        self.led_controller.set_listening_mode()

        # Start a timeout thread
        threading.Thread(target=self._listening_timeout).start()

    def _on_recording(self, context: dict):
        family_member = context.get('family_member', 'UNKNOWN')
        print(f"State: Recording message for {family_member}")
        self.led_controller.set_recording_mode()

        # Start recording
        filename = self.file_manager.generate_filename(family_member)
        file_path = self.file_manager.get_file_path(filename)

        self.current_recording_member = family_member
        self.current_recording_file = file_path

        success = self.audio_recorder.start_recording(file_path)
        if not success:
            print("Failed to start recording")
            self.state_machine.transition_to(MuninnState.SLEEPING)

    def _on_playing(self, context: dict):
        family_member = context.get('family_member')
        print(f"State: Playing messages for {family_member}")

        if family_member:
            self.led_controller.illuminate_family_member(family_member, (0, 255, 0))
            self._play_messages_for_member(family_member)
        else:
            self.led_controller.set_listening_mode()
            self._play_recent_messages()

    def _on_processing(self, context: dict):
        print("State: Processing recorded message")
        self.led_controller.set_listening_mode()

    def _on_recording_finished(self, old_state, new_state, context: dict):
        if self.current_recording_file and self.current_recording_member:
            # Save to database
            duration = self.file_manager.get_audio_duration(self.current_recording_file)
            message_id = self.database.add_message(
                self.current_recording_member,
                os.path.basename(self.current_recording_file),
                self.current_recording_file,
                duration
            )

            print(f"Message saved with ID: {message_id}")

            # Try to transcribe
            transcription = self.speech_processor.transcribe_audio_file(self.current_recording_file)
            if transcription:
                self.database.update_message_transcription(message_id, transcription)
                print(f"Transcription: {transcription}")

        # Clear recording state
        self.current_recording_member = None
        self.current_recording_file = None

        # Return to sleeping state
        threading.Timer(2.0, lambda: self.state_machine.transition_to(MuninnState.SLEEPING)).start()

    # Event handlers
    def on_wake_word_detected(self):
        if self.state_machine.is_state(MuninnState.SLEEPING):
            print("Wake word detected!")
            self.state_machine.transition_to(MuninnState.LISTENING)

    def _listening_timeout(self):
        time.sleep(10)  # 10 second timeout
        if self.state_machine.is_state(MuninnState.LISTENING):
            print("Listening timeout - returning to sleep")
            self.state_machine.transition_to(MuninnState.SLEEPING)

    def _play_messages_for_member(self, family_member: str):
        messages = self.database.get_messages_by_family_member(family_member, limit=5)
        if not messages:
            print(f"No messages found for {family_member}")
            threading.Timer(2.0, lambda: self.state_machine.transition_to(MuninnState.SLEEPING)).start()
            return

        def play_next_message(index=0):
            if index >= len(messages):
                print("Finished playing all messages")
                self.state_machine.transition_to(MuninnState.SLEEPING)
                return

            message = messages[index]
            file_path = message['file_path']

            if self.file_manager.file_exists(file_path):
                print(f"Playing message {index + 1}/{len(messages)}")
                self.audio_player.play_file(
                    file_path,
                    lambda: play_next_message(index + 1)
                )
            else:
                print(f"File not found: {file_path}")
                play_next_message(index + 1)

        play_next_message()

    def _play_recent_messages(self):
        messages = self.database.get_recent_messages(days=7)
        if not messages:
            print("No recent messages found")
            threading.Timer(2.0, lambda: self.state_machine.transition_to(MuninnState.SLEEPING)).start()
            return

        # Play the most recent message
        message = messages[0]
        file_path = message['file_path']

        if self.file_manager.file_exists(file_path):
            print(f"Playing recent message from {message['family_member']}")
            self.audio_player.play_file(
                file_path,
                lambda: self.state_machine.transition_to(MuninnState.SLEEPING)
            )
        else:
            print(f"File not found: {file_path}")
            self.state_machine.transition_to(MuninnState.SLEEPING)

    # Command processing (for future keyboard commands)
    def process_text_command(self, text: str):
        command, target = self.speech_processor.process_command(text)

        if command == "record":
            if not target:
                print("Please specify a family member name")
                return
            self.state_machine.transition_to(MuninnState.RECORDING, {'family_member': target})

        elif command == "play":
            if target and target in FAMILY_MEMBERS:
                self.state_machine.transition_to(MuninnState.PLAYING, {'family_member': target})
            else:
                self.state_machine.transition_to(MuninnState.PLAYING, {})

        elif command == "stop":
            self.audio_recorder.stop_recording()
            self.audio_player.stop_playback()
            self.state_machine.transition_to(MuninnState.SLEEPING)

        elif command == "list":
            self._list_messages()

        elif command == "help":
            self._show_help()

        else:
            print(f"Unknown command: {text}")

    def _list_messages(self):
        counts = self.database.get_family_member_count()
        print("\nMessage counts by family member:")
        for member, count in counts.items():
            print(f"  {member}: {count} messages")
        print()

    def _show_help(self):
        print("\nMuninn Voice Commands:")
        print("  'Muninn, remember this' - Start recording")
        print("  'Muninn, play [name]'s messages' - Play messages")
        print("  'Muninn, stop' - Stop current operation")
        print("  'Muninn, list' - Show message counts")
        print()

def main():
    try:
        assistant = MuninnVoiceAssistant()
        assistant.start()
    except Exception as e:
        print(f"Error starting Muninn: {e}")
        return 1

    return 0

if __name__ == "__main__":
    sys.exit(main())