"""
Image Handler Module
Validates images and generates new ones with DALL-E if needed.
"""

from openai import OpenAI
import requests
from typing import Optional
import config


class ImageHandler:
    """Handle image extraction and generation."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def get_or_generate_image(self, image_url: Optional[str], title: str, summary: str) -> Optional[str]:
        """
        Get existing image or generate a new one.

        Args:
            image_url: URL of existing image (may be None)
            title: Post title
            summary: Post summary

        Returns:
            URL of valid image or generated image
        """
        # First, try to validate existing image
        if image_url and self._validate_image_url(image_url):
            print(f"✓ Using existing image: {image_url[:50]}...")
            return image_url

        # Generate new image if configured to do so
        if config.GENERATE_IMAGE_IF_NOT_FOUND:
            print("⚙ Generating image with DALL-E...")
            return self._generate_image(title, summary)

        return None

    def _validate_image_url(self, url: str) -> bool:
        """Check if image URL is accessible."""
        try:
            response = requests.head(url, timeout=5, allow_redirects=True)
            content_type = response.headers.get('content-type', '')
            return response.status_code == 200 and 'image' in content_type
        except:
            return False

    def _generate_image(self, title: str, summary: str) -> Optional[str]:
        """Generate an image using DALL-E."""
        try:
            # Create prompt for image generation
            prompt = self._create_image_prompt(title, summary)

            # Generate image with DALL-E
            response = self.client.images.generate(
                model=config.OPENAI_IMAGE_MODEL,
                prompt=prompt,
                size="1024x1024",
                quality="standard",
                n=1
            )

            image_url = response.data[0].url
            print(f"✓ Generated image with DALL-E")
            return image_url

        except Exception as e:
            print(f"✗ Error generating image: {e}")
            return None

    def _create_image_prompt(self, title: str, summary: str) -> str:
        """Create a prompt for DALL-E based on title and summary."""
        # Keep it simple and descriptive
        prompt = f"A professional, modern illustration representing: {title}. {summary[:100]}"
        # Limit prompt length
        return prompt[:400]


def handle_image(image_url: Optional[str], title: str, summary: str) -> Optional[str]:
    """Convenience function to handle images."""
    handler = ImageHandler()
    return handler.get_or_generate_image(image_url, title, summary)


if __name__ == '__main__':
    # Test the handler
    result = handle_image(
        None,
        "ChatGPT Release",
        "OpenAI releases a new conversational AI model"
    )
    print(f"\nImage URL: {result}")
