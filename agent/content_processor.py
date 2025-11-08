"""
Content Processor Module
Uses OpenAI to generate summaries and process content.
"""

from openai import OpenAI
from typing import Dict
from datetime import datetime
from urllib.parse import urlparse
import config


class ContentProcessor:
    """Process content using OpenAI API."""

    def __init__(self):
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)

    def process_content(self, scraped_data: Dict) -> Dict:
        """
        Process scraped content to create a structured post.

        Args:
            scraped_data: Data from web_scraper

        Returns:
            Dict with title, summary, provider, type
        """
        result = {
            'title': scraped_data.get('title', 'Sin título'),
            'summary': None,
            'provider': self._extract_provider(scraped_data['url']),
            'type': 'Artículo',
            'success': False
        }

        try:
            # Generate summary using OpenAI
            if scraped_data.get('content'):
                result['summary'] = self._generate_summary(
                    scraped_data['title'],
                    scraped_data['content']
                )
            else:
                result['summary'] = scraped_data.get('og_data', {}).get('description', 'Sin descripción disponible')

            result['success'] = True
            print(f"✓ Processed content for: {result['title'][:50]}...")

        except Exception as e:
            result['summary'] = f"Error procesando contenido: {e}"
            print(f"✗ Error processing content: {e}")

        return result

    def _generate_summary(self, title: str, content: str) -> str:
        """Generate a 2-3 line summary using OpenAI."""
        try:
            response = self.client.chat.completions.create(
                model=config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un asistente que crea resúmenes concisos de artículos. Responde en español con un resumen de 2-3 líneas máximo."
                    },
                    {
                        "role": "user",
                        "content": f"Resume este artículo en 2-3 líneas:\n\nTítulo: {title}\n\nContenido: {content[:1500]}"
                    }
                ],
                max_tokens=150,
                temperature=0.7
            )

            summary = response.choices[0].message.content.strip()
            return summary

        except Exception as e:
            print(f"Warning: Error generating summary with OpenAI: {e}")
            return f"{title}. Contenido disponible en el enlace."

    def _extract_provider(self, url: str) -> str:
        """Extract provider name from URL."""
        try:
            domain = urlparse(url).netloc
            # Remove www. and .com/.org/etc
            provider = domain.replace('www.', '').split('.')[0]
            return provider.capitalize()
        except:
            return "Web"


def process_scraped_content(scraped_data: Dict) -> Dict:
    """Convenience function to process content."""
    processor = ContentProcessor()
    return processor.process_content(scraped_data)


if __name__ == '__main__':
    # Test the processor
    test_data = {
        'url': 'https://openai.com/blog/chatgpt',
        'title': 'ChatGPT: Optimizing Language Models',
        'content': "We've trained a model called ChatGPT which interacts in a conversational way...",
        'og_data': {}
    }

    result = process_scraped_content(test_data)
    print(f"\nTitle: {result['title']}")
    print(f"Summary: {result['summary']}")
    print(f"Provider: {result['provider']}")
