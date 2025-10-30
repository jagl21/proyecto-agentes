"""
API Client Module
Communicates with Flask backend to create pending posts.
"""

import requests
from typing import Dict
from datetime import datetime
import config


class APIClient:
    """Client for Flask API communication."""

    def __init__(self):
        self.base_url = config.FLASK_PENDING_POSTS_ENDPOINT

    def create_pending_post(self, post_data: Dict) -> Dict:
        """
        Create a pending post in the backend.

        Args:
            post_data: Dictionary with post information

        Returns:
            Response from API
        """
        try:
            response = requests.post(
                self.base_url,
                json=post_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            result = response.json()

            if response.status_code == 201 and result.get('success'):
                print(f"✓ Created pending post: {post_data['title'][:50]}...")
                return result
            else:
                print(f"✗ Failed to create post: {result.get('error', 'Unknown error')}")
                return result

        except Exception as e:
            print(f"✗ Error calling API: {e}")
            return {'success': False, 'error': str(e)}


def create_pending_post(title: str, summary: str, source_url: str,
                       image_url: str = None, provider: str = None,
                       type: str = None) -> Dict:
    """
    Convenience function to create a pending post.

    Args:
        title: Post title
        summary: Post summary
        source_url: Original URL
        image_url: Image URL (optional)
        provider: Content provider (optional)
        type: Content type (optional)

    Returns:
        API response
    """
    client = APIClient()

    post_data = {
        'title': title,
        'summary': summary,
        'source_url': source_url,
        'image_url': image_url,
        'release_date': datetime.now().strftime('%Y-%m-%d'),
        'provider': provider,
        'type': type
    }

    return client.create_pending_post(post_data)


if __name__ == '__main__':
    # Test the client
    result = create_pending_post(
        title="Test Post from Agent",
        summary="This is a test post created by the AI agent",
        source_url="https://example.com",
        provider="Test Provider",
        type="Test"
    )

    print(f"\nResult: {result}")
