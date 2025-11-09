"""
Image Handler Module
Validates images and generates new ones with DALL-E if needed.
Downloads and saves generated images locally.
"""

from openai import OpenAI
import requests
from typing import Optional
from pathlib import Path
import uuid
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
        """Generate an image using DALL-E and save it locally."""
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

            # Get temporary DALL-E URL
            dalle_url = response.data[0].url
            print(f"✓ Generated image with DALL-E")

            # Download and save the image locally
            local_url = self._download_and_save_image(dalle_url)

            if local_url:
                print(f"✓ Image saved locally: {local_url}")
                return local_url
            else:
                # Fallback to DALL-E URL if download fails
                print("⚠ Failed to save locally, using DALL-E URL")
                return dalle_url

        except Exception as e:
            print(f"✗ Error generating image: {e}")
            return None

    def _download_and_save_image(self, image_url: str) -> Optional[str]:
        """
        Download image from URL and save locally.

        Args:
            image_url: URL of the image to download

        Returns:
            Local URL path (/images/generated/{uuid}.png) or None if failed
        """
        try:
            # Generate unique filename
            filename = f"{uuid.uuid4()}.png"

            # Path to frontend images directory (relative from agent/ directory)
            save_dir = Path(__file__).parent.parent / 'frontend' / 'images' / 'generated'

            # Create directory if doesn't exist
            save_dir.mkdir(parents=True, exist_ok=True)

            # Download image
            print(f"  Downloading image from DALL-E...")
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()

            # Save to file
            filepath = save_dir / filename
            filepath.write_bytes(response.content)

            print(f"  Saved to: {filepath}")

            # Return URL path for Flask (not filesystem path)
            return f"/images/generated/{filename}"

        except Exception as e:
            print(f"  ✗ Error downloading image: {e}")
            return None

    def _clean_title_for_prompt(self, title: str) -> str:
        """
        Clean title by removing site names and noise.

        Args:
            title: Original article title

        Returns:
            Cleaned title suitable for DALL-E prompt
        """
        # Remove common site names and noise words
        sites_to_remove = [
            'The Guardian', 'BBC', 'CNN', 'Reuters', 'Bloomberg',
            'TechCrunch', 'Wired', 'The Verge', 'Ars Technica',
            'New York Times', 'Washington Post', 'Forbes', 'Medium',
            'Page Not Found', 'Error', '404', 'Not Found'
        ]

        cleaned = title
        for site in sites_to_remove:
            # Case-insensitive replacement
            cleaned = cleaned.replace(site, '')
            cleaned = cleaned.replace(site.lower(), '')

        # Remove common separators and extra spaces
        cleaned = cleaned.replace(' | ', ' ').replace(' - ', ' ').replace('|', '').replace('-', '')

        # Normalize whitespace
        cleaned = ' '.join(cleaned.split())

        return cleaned.strip()

    def _create_image_prompt(self, title: str, summary: str) -> str:
        """
        Create an optimized prompt for DALL-E based on title and summary.

        Args:
            title: Article title
            summary: Article summary

        Returns:
            Optimized prompt for DALL-E image generation
        """
        # Clean title: remove site names and noise
        cleaned_title = self._clean_title_for_prompt(title)

        # Build structured prompt with visual guidelines
        prompt = (
            f"Professional editorial illustration for news article. "
            f"Topic: {cleaned_title}. "
            f"{summary[:150]}. "
            f"Style: Modern, clean, minimalist, professional journalism. "
            f"Format: Horizontal banner, centered composition. "
            f"Colors: Balanced and professional. "
            f"Avoid: Text, logos, watermarks."
        )

        # Limit to 400 chars
        final_prompt = prompt[:400]

        # Log prompt for debugging
        print(f"  [DALL-E Prompt] {final_prompt}")

        return final_prompt


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
