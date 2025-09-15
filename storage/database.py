import sqlite3
import datetime
from typing import List, Optional, Dict, Any
from config.settings import Settings

class DatabaseManager:
    def __init__(self):
        self.db_path = Settings.DATABASE_PATH
        self.init_database()

    def init_database(self):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    family_member TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    duration_seconds REAL,
                    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    transcription TEXT,
                    tags TEXT,
                    is_archived BOOLEAN DEFAULT FALSE
                )
            ''')

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_family_member ON messages(family_member)
            ''')

            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_recorded_at ON messages(recorded_at)
            ''')

            conn.commit()

    def add_message(self, family_member: str, filename: str, file_path: str,
                   duration_seconds: Optional[float] = None,
                   transcription: Optional[str] = None,
                   tags: Optional[str] = None) -> int:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO messages (family_member, filename, file_path, duration_seconds, transcription, tags)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (family_member.upper(), filename, file_path, duration_seconds, transcription, tags))
            conn.commit()
            return cursor.lastrowid

    def get_messages_by_family_member(self, family_member: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT * FROM messages
                WHERE family_member = ? AND is_archived = FALSE
                ORDER BY recorded_at DESC
            '''

            if limit:
                query += f' LIMIT {limit}'

            cursor.execute(query, (family_member.upper(),))
            return [dict(row) for row in cursor.fetchall()]

    def get_all_messages(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = '''
                SELECT * FROM messages
                WHERE is_archived = FALSE
                ORDER BY recorded_at DESC
            '''

            if limit:
                query += f' LIMIT {limit}'

            cursor.execute(query)
            return [dict(row) for row in cursor.fetchall()]

    def get_recent_messages(self, days: int = 7) -> List[Dict[str, Any]]:
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages
                WHERE recorded_at >= ? AND is_archived = FALSE
                ORDER BY recorded_at DESC
            ''', (cutoff_date,))
            return [dict(row) for row in cursor.fetchall()]

    def update_message_transcription(self, message_id: int, transcription: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages
                SET transcription = ?
                WHERE id = ?
            ''', (transcription, message_id))
            conn.commit()

    def archive_message(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE messages
                SET is_archived = TRUE
                WHERE id = ?
            ''', (message_id,))
            conn.commit()

    def delete_message(self, message_id: int):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM messages WHERE id = ?', (message_id,))
            conn.commit()

    def get_family_member_count(self) -> Dict[str, int]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT family_member, COUNT(*) as count
                FROM messages
                WHERE is_archived = FALSE
                GROUP BY family_member
                ORDER BY count DESC
            ''')
            return {row[0]: row[1] for row in cursor.fetchall()}

    def search_messages(self, query: str) -> List[Dict[str, Any]]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM messages
                WHERE (transcription LIKE ? OR tags LIKE ?) AND is_archived = FALSE
                ORDER BY recorded_at DESC
            ''', (f'%{query}%', f'%{query}%'))
            return [dict(row) for row in cursor.fetchall()]

    def set_setting(self, key: str, value: str):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            ''', (key, value))
            conn.commit()

    def get_setting(self, key: str, default: Optional[str] = None) -> Optional[str]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default