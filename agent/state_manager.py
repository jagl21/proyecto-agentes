"""
State Manager Module
Manages persistence of processed messages to avoid duplicates.
"""

import sqlite3
from datetime import datetime
from typing import Optional
import os


class StateManager:
    """Manage agent state persistence using SQLite."""

    def __init__(self, db_path: str = 'agent_state.db'):
        """
        Initialize state manager.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize state database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create processed_messages table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS processed_messages (
                message_id INTEGER PRIMARY KEY,
                chat_id TEXT NOT NULL,
                url TEXT,
                processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'processed',
                error_message TEXT
            )
        ''')

        # Create index for faster lookups
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_message_id
            ON processed_messages(message_id)
        ''')

        conn.commit()
        conn.close()
        print(f"✓ State database initialized: {self.db_path}")

    def is_message_processed(self, message_id: int) -> bool:
        """
        Check if a message was already processed.

        Args:
            message_id: Telegram message ID

        Returns:
            True if message was already processed
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            'SELECT 1 FROM processed_messages WHERE message_id = ?',
            (message_id,)
        )
        result = cursor.fetchone()
        conn.close()

        return result is not None

    def mark_message_processed(
        self,
        message_id: int,
        chat_id: str,
        url: Optional[str] = None,
        status: str = 'processed',
        error: Optional[str] = None
    ):
        """
        Mark a message as processed.

        Args:
            message_id: Telegram message ID
            chat_id: Telegram chat ID
            url: URL that was processed
            status: Processing status ('processed', 'failed', 'skipped')
            error: Error message if status is 'failed'
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            INSERT OR REPLACE INTO processed_messages
            (message_id, chat_id, url, processed_at, status, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (message_id, chat_id, url, datetime.now(), status, error))

        conn.commit()
        conn.close()

    def get_failed_count(self) -> int:
        """
        Get count of messages that failed processing.

        Returns:
            Number of failed messages
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT COUNT(*) FROM processed_messages WHERE status = 'failed'"
        )
        count = cursor.fetchone()[0]
        conn.close()

        return count

    def get_processed_count(self) -> int:
        """
        Get total count of processed messages.

        Returns:
            Total number of processed messages
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM processed_messages")
        count = cursor.fetchone()[0]
        conn.close()

        return count

    def cleanup_old_records(self, days: int = 30):
        """
        Remove records older than N days to prevent database bloat.

        Args:
            days: Number of days to keep records
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            DELETE FROM processed_messages
            WHERE processed_at < datetime('now', '-' || ? || ' days')
        ''', (days,))

        deleted = cursor.rowcount
        conn.commit()
        conn.close()

        if deleted > 0:
            print(f"✓ Cleaned up {deleted} old records")

    def get_stats(self) -> dict:
        """
        Get processing statistics.

        Returns:
            Dictionary with statistics
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get counts by status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM processed_messages
            GROUP BY status
        ''')
        status_counts = {row[0]: row[1] for row in cursor.fetchall()}

        # Get total
        cursor.execute('SELECT COUNT(*) FROM processed_messages')
        total = cursor.fetchone()[0]

        conn.close()

        return {
            'total': total,
            'processed': status_counts.get('processed', 0),
            'failed': status_counts.get('failed', 0),
            'skipped': status_counts.get('skipped', 0)
        }


if __name__ == '__main__':
    # Test the state manager
    print("Testing StateManager...")

    manager = StateManager('test_state.db')

    # Test marking messages
    manager.mark_message_processed(
        message_id=12345,
        chat_id='-1001234567890',
        url='https://example.com',
        status='processed'
    )

    # Test checking
    is_processed = manager.is_message_processed(12345)
    print(f"Message 12345 processed: {is_processed}")

    # Test stats
    stats = manager.get_stats()
    print(f"Stats: {stats}")

    # Cleanup
    if os.path.exists('test_state.db'):
        os.remove('test_state.db')

    print("✓ Tests completed")
