"""
Data models and validation for the posts application.
"""

from typing import Dict, Any, Optional
from datetime import datetime


class Post:
    """
    Post model representing a news article or post.
    """

    def __init__(
        self,
        title: str,
        summary: str,
        source_url: str,
        release_date: str,
        image_url: Optional[str] = None,
        provider: Optional[str] = None,
        type: Optional[str] = None,
        id: Optional[int] = None,
        created_at: Optional[str] = None
    ):
        self.id = id
        self.title = title
        self.summary = summary
        self.source_url = source_url
        self.image_url = image_url
        self.release_date = release_date
        self.provider = provider
        self.type = type
        self.created_at = created_at

    @staticmethod
    def validate_post_data(data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate post data before insertion.

        Args:
            data: Dictionary containing post data

        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ['title', 'summary', 'source_url', 'release_date']

        # Check for required fields
        for field in required_fields:
            if field not in data:
                return False, f"Missing required field: {field}"
            if not data[field] or str(data[field]).strip() == '':
                return False, f"Field '{field}' cannot be empty"

        # Validate title length
        if len(data['title']) > 500:
            return False, "Title is too long (max 500 characters)"

        # Validate summary length
        if len(data['summary']) > 2000:
            return False, "Summary is too long (max 2000 characters)"

        # Validate URL format (basic check)
        source_url = data['source_url']
        if not source_url.startswith('http://') and not source_url.startswith('https://'):
            return False, "Invalid source_url format (must start with http:// or https://)"

        # Validate image_url if provided
        if 'image_url' in data and data['image_url']:
            image_url = data['image_url']
            # Allow absolute URLs (http://, https://) or relative paths (starting with /)
            if not (image_url.startswith('http://') or
                    image_url.startswith('https://') or
                    image_url.startswith('/')):
                return False, "Invalid image_url format (must be absolute URL or relative path)"

        return True, ""

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert post object to dictionary.

        Returns:
            Dictionary representation of the post
        """
        return {
            'id': self.id,
            'title': self.title,
            'summary': self.summary,
            'source_url': self.source_url,
            'image_url': self.image_url,
            'release_date': self.release_date,
            'provider': self.provider,
            'type': self.type,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Post':
        """
        Create a Post instance from a dictionary.

        Args:
            data: Dictionary containing post data

        Returns:
            Post instance
        """
        return cls(
            id=data.get('id'),
            title=data['title'],
            summary=data['summary'],
            source_url=data['source_url'],
            image_url=data.get('image_url'),
            release_date=data['release_date'],
            provider=data.get('provider'),
            type=data.get('type'),
            created_at=data.get('created_at')
        )
