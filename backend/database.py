"""
Database management module for the posts application.
Handles SQLite database initialization and CRUD operations.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any

DATABASE_NAME = 'posts.db'


def get_connection():
    """
    Create and return a database connection.

    Returns:
        sqlite3.Connection: Database connection object
    """
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def init_database():
    """
    Initialize the database and create the posts table if it doesn't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            source_url TEXT NOT NULL,
            image_url TEXT,
            release_date TEXT NOT NULL,
            provider TEXT,
            type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")


def create_post(post_data: Dict[str, Any]) -> int:
    """
    Insert a new post into the database.

    Args:
        post_data: Dictionary containing post information

    Returns:
        int: ID of the newly created post

    Raises:
        ValueError: If required fields are missing
    """
    required_fields = ['title', 'summary', 'source_url', 'release_date']
    for field in required_fields:
        if field not in post_data or not post_data[field]:
            raise ValueError(f"Missing required field: {field}")

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        INSERT INTO posts (title, summary, source_url, image_url, release_date, provider, type)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data['title'],
        post_data['summary'],
        post_data['source_url'],
        post_data.get('image_url'),
        post_data['release_date'],
        post_data.get('provider'),
        post_data.get('type')
    ))

    post_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return post_id


def get_all_posts() -> List[Dict[str, Any]]:
    """
    Retrieve all posts from the database, ordered by creation date (newest first).

    Returns:
        List of dictionaries containing post data
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, summary, source_url, image_url, release_date,
               provider, type, created_at
        FROM posts
        ORDER BY created_at DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    # Convert rows to dictionaries
    posts = []
    for row in rows:
        posts.append({
            'id': row['id'],
            'title': row['title'],
            'summary': row['summary'],
            'source_url': row['source_url'],
            'image_url': row['image_url'],
            'release_date': row['release_date'],
            'provider': row['provider'],
            'type': row['type'],
            'created_at': row['created_at']
        })

    return posts


def get_post_by_id(post_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific post by its ID.

    Args:
        post_id: The ID of the post to retrieve

    Returns:
        Dictionary containing post data, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, summary, source_url, image_url, release_date,
               provider, type, created_at
        FROM posts
        WHERE id = ?
    ''', (post_id,))

    row = cursor.fetchone()
    conn.close()

    if row is None:
        return None

    return {
        'id': row['id'],
        'title': row['title'],
        'summary': row['summary'],
        'source_url': row['source_url'],
        'image_url': row['image_url'],
        'release_date': row['release_date'],
        'provider': row['provider'],
        'type': row['type'],
        'created_at': row['created_at']
    }


if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
