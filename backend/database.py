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
    Initialize the database and create the posts and pending_posts tables if they don't exist.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create posts table (public posts)
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

    # Create pending_posts table (posts awaiting approval)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pending_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            summary TEXT NOT NULL,
            source_url TEXT NOT NULL,
            image_url TEXT,
            release_date TEXT NOT NULL,
            provider TEXT,
            type TEXT,
            status TEXT DEFAULT 'pending',
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


# ============================================
# CRUD Operations for pending_posts
# ============================================

def create_pending_post(post_data: Dict[str, Any]) -> int:
    """
    Insert a new pending post into the database.

    Args:
        post_data: Dictionary containing post information

    Returns:
        int: ID of the newly created pending post

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
        INSERT INTO pending_posts (title, summary, source_url, image_url, release_date, provider, type, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        post_data['title'],
        post_data['summary'],
        post_data['source_url'],
        post_data.get('image_url'),
        post_data['release_date'],
        post_data.get('provider'),
        post_data.get('type'),
        post_data.get('status', 'pending')
    ))

    post_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return post_id


def get_all_pending_posts(status: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Retrieve all pending posts from the database, optionally filtered by status.

    Args:
        status: Optional status filter ('pending', 'approved', 'rejected')

    Returns:
        List of dictionaries containing pending post data
    """
    conn = get_connection()
    cursor = conn.cursor()

    if status:
        cursor.execute('''
            SELECT id, title, summary, source_url, image_url, release_date,
                   provider, type, status, created_at
            FROM pending_posts
            WHERE status = ?
            ORDER BY created_at DESC
        ''', (status,))
    else:
        cursor.execute('''
            SELECT id, title, summary, source_url, image_url, release_date,
                   provider, type, status, created_at
            FROM pending_posts
            ORDER BY created_at DESC
        ''')

    rows = cursor.fetchall()
    conn.close()

    # Convert rows to dictionaries
    pending_posts = []
    for row in rows:
        pending_posts.append({
            'id': row['id'],
            'title': row['title'],
            'summary': row['summary'],
            'source_url': row['source_url'],
            'image_url': row['image_url'],
            'release_date': row['release_date'],
            'provider': row['provider'],
            'type': row['type'],
            'status': row['status'],
            'created_at': row['created_at']
        })

    return pending_posts


def get_pending_post_by_id(post_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve a specific pending post by its ID.

    Args:
        post_id: The ID of the pending post to retrieve

    Returns:
        Dictionary containing pending post data, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, title, summary, source_url, image_url, release_date,
               provider, type, status, created_at
        FROM pending_posts
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
        'status': row['status'],
        'created_at': row['created_at']
    }


def update_pending_post(post_id: int, update_data: Dict[str, Any]) -> bool:
    """
    Update a pending post's information.

    Args:
        post_id: The ID of the pending post to update
        update_data: Dictionary containing fields to update

    Returns:
        bool: True if update was successful, False if post not found
    """
    # Build dynamic UPDATE query based on provided fields
    allowed_fields = ['title', 'summary', 'source_url', 'image_url', 'release_date', 'provider', 'type', 'status']
    update_fields = {k: v for k, v in update_data.items() if k in allowed_fields}

    if not update_fields:
        return False

    conn = get_connection()
    cursor = conn.cursor()

    # Build SET clause
    set_clause = ', '.join([f"{field} = ?" for field in update_fields.keys()])
    values = list(update_fields.values()) + [post_id]

    cursor.execute(f'''
        UPDATE pending_posts
        SET {set_clause}
        WHERE id = ?
    ''', values)

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected > 0


def approve_pending_post(post_id: int) -> Optional[int]:
    """
    Approve a pending post: move it to posts table and update status.

    Args:
        post_id: The ID of the pending post to approve

    Returns:
        int: ID of the newly created post in posts table, or None if failed
    """
    # Get the pending post
    pending_post = get_pending_post_by_id(post_id)

    if not pending_post:
        return None

    # Create the post in posts table
    try:
        new_post_id = create_post(pending_post)

        # Update status in pending_posts
        update_pending_post(post_id, {'status': 'approved'})

        return new_post_id
    except Exception as e:
        print(f"Error approving pending post: {e}")
        return None


def reject_pending_post(post_id: int) -> bool:
    """
    Reject a pending post by updating its status.
    If the post was already approved, also delete it from posts table (unpublish).

    Args:
        post_id: The ID of the pending post to reject

    Returns:
        bool: True if rejection was successful, False otherwise
    """
    # Get the pending post to check its current status
    pending_post = get_pending_post_by_id(post_id)

    if not pending_post:
        return False

    # If status is 'approved', the post is published - we need to unpublish it
    if pending_post.get('status') == 'approved':
        try:
            conn = get_connection()
            cursor = conn.cursor()

            # Find and delete the published post by source_url (should be unique)
            cursor.execute('''
                DELETE FROM posts
                WHERE source_url = ?
            ''', (pending_post['source_url'],))

            deleted_count = cursor.rowcount
            conn.commit()
            conn.close()

            if deleted_count > 0:
                print(f"✓ Unpublished post: {pending_post['source_url']}")
        except Exception as e:
            print(f"Warning: Could not delete published post: {e}")
            # Continue anyway to mark as rejected in pending_posts

    # Update status to rejected in pending_posts
    return update_pending_post(post_id, {'status': 'rejected'})


def delete_pending_post(post_id: int) -> bool:
    """
    Delete a pending post from the database.

    Args:
        post_id: The ID of the pending post to delete

    Returns:
        bool: True if deletion was successful, False if post not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('DELETE FROM pending_posts WHERE id = ?', (post_id,))

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()

    return rows_affected > 0


if __name__ == '__main__':
    # Initialize database when run directly
    init_database()
