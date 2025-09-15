import os
import wave
import datetime
from typing import Optional
from config.settings import Settings

class FileManager:
    def __init__(self):
        Settings.ensure_directories()

    def generate_filename(self, family_member: str, extension: str = "wav") -> str:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = "".join(c for c in family_member if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').upper()
        return f"{safe_name}_{timestamp}.{extension}"

    def get_file_path(self, filename: str) -> str:
        return os.path.join(Settings.AUDIO_DIR, filename)

    def file_exists(self, filepath: str) -> bool:
        return os.path.exists(filepath)

    def get_audio_duration(self, filepath: str) -> Optional[float]:
        try:
            with wave.open(filepath, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                duration = frames / float(sample_rate)
                return duration
        except Exception as e:
            print(f"Error getting audio duration for {filepath}: {e}")
            return None

    def organize_by_family_member(self, family_member: str) -> str:
        member_dir = os.path.join(Settings.AUDIO_DIR, family_member.upper())
        os.makedirs(member_dir, exist_ok=True)
        return member_dir

    def get_all_audio_files(self) -> list:
        audio_files = []
        for root, dirs, files in os.walk(Settings.AUDIO_DIR):
            for file in files:
                if file.lower().endswith(('.wav', '.mp3', '.m4a', '.flac')):
                    audio_files.append(os.path.join(root, file))
        return audio_files

    def delete_file(self, filepath: str) -> bool:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            print(f"Error deleting file {filepath}: {e}")
            return False

    def get_file_size(self, filepath: str) -> Optional[int]:
        try:
            return os.path.getsize(filepath)
        except Exception:
            return None

    def cleanup_old_files(self, days_old: int = 365):
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days_old)

        for audio_file in self.get_all_audio_files():
            try:
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(audio_file))
                if file_time < cutoff_date:
                    print(f"Cleaning up old file: {audio_file}")
                    self.delete_file(audio_file)
            except Exception as e:
                print(f"Error during cleanup of {audio_file}: {e}")

    def get_storage_stats(self) -> dict:
        total_files = 0
        total_size = 0

        for audio_file in self.get_all_audio_files():
            total_files += 1
            size = self.get_file_size(audio_file)
            if size:
                total_size += size

        return {
            'total_files': total_files,
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2)
        }