"""
Web Scraper Module
Uses Playwright to navigate URLs and extract content.
"""

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from typing import Dict, Optional
import config


class WebScraper:
    """Scrape web content using Playwright."""

    async def scrape_url(self, url: str) -> Dict:
        """
        Scrape a URL and extract content.

        Args:
            url: URL to scrape

        Returns:
            Dict with title, content, image_url, and metadata
        """
        result = {
            'url': url,
            'title': None,
            'content': None,
            'image_url': None,
            'og_data': {},
            'success': False,
            'error': None
        }

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=config.HEADLESS)
                page = await browser.new_page(user_agent=config.USER_AGENT)

                # Navigate to URL
                await page.goto(url, timeout=config.BROWSER_TIMEOUT, wait_until='domcontentloaded')

                # Wait a bit for dynamic content
                await page.wait_for_timeout(2000)

                # Get page content
                html = await page.content()

                # Extract OpenGraph and meta tags
                result['og_data'] = await self._extract_meta_tags(page)

                # Parse with BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')

                # Extract title
                result['title'] = self._extract_title(soup, result['og_data'])

                # Extract main content
                result['content'] = self._extract_content(soup)

                # Extract image URL
                result['image_url'] = self._extract_image_url(soup, result['og_data'])

                await browser.close()

                result['success'] = True
                print(f"✓ Scraped: {url[:50]}...")

        except Exception as e:
            result['error'] = str(e)
            print(f"✗ Error scraping {url}: {e}")

        return result

    async def _extract_meta_tags(self, page) -> Dict:
        """Extract OpenGraph and Twitter Card meta tags."""
        og_data = {}

        try:
            # OpenGraph tags
            og_title = await page.query_selector('meta[property="og:title"]')
            if og_title:
                og_data['title'] = await og_title.get_attribute('content')

            og_description = await page.query_selector('meta[property="og:description"]')
            if og_description:
                og_data['description'] = await og_description.get_attribute('content')

            og_image = await page.query_selector('meta[property="og:image"]')
            if og_image:
                og_data['image'] = await og_image.get_attribute('content')

            # Twitter Card tags
            twitter_image = await page.query_selector('meta[name="twitter:image"]')
            if twitter_image and 'image' not in og_data:
                og_data['image'] = await twitter_image.get_attribute('content')

        except Exception as e:
            print(f"Warning: Error extracting meta tags: {e}")

        return og_data

    def _extract_title(self, soup: BeautifulSoup, og_data: Dict) -> str:
        """Extract title from page."""
        # Try OpenGraph first
        if og_data.get('title'):
            return og_data['title']

        # Try <title> tag
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Try h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text().strip()

        return "Sin título"

    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from page."""
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()

        # Try common article containers
        article = soup.find('article')
        if article:
            text = article.get_text(separator=' ', strip=True)
            return text[:2000]  # Limit to 2000 chars

        # Try main content
        main = soup.find('main')
        if main:
            text = main.get_text(separator=' ', strip=True)
            return text[:2000]

        # Fallback to body
        body = soup.find('body')
        if body:
            text = body.get_text(separator=' ', strip=True)
            return text[:2000]

        return ""

    def _extract_image_url(self, soup: BeautifulSoup, og_data: Dict) -> Optional[str]:
        """Extract image URL from page."""
        # Try OpenGraph image first
        if og_data.get('image'):
            return og_data['image']

        # Try first img in article
        article = soup.find('article')
        if article:
            img = article.find('img')
            if img and img.get('src'):
                return img['src']

        # Try any img with decent size attributes
        for img in soup.find_all('img'):
            src = img.get('src')
            width = img.get('width', '0')
            if src and (not width or int(width.replace('px', '').replace('%', '').split()[0] if width else 0) > 200):
                return src

        return None


async def scrape_url(url: str) -> Dict:
    """Convenience function to scrape a single URL."""
    scraper = WebScraper()
    return await scraper.scrape_url(url)


if __name__ == '__main__':
    import asyncio

    # Test the scraper
    async def test():
        test_url = "https://openai.com/blog"
        result = await scrape_url(test_url)
        print(f"\nTitle: {result['title']}")
        print(f"Content: {result['content'][:200]}...")
        print(f"Image: {result['image_url']}")

    asyncio.run(test())
