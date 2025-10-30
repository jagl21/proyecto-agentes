"""
Telegram Monitor Module
Connects to Telegram and extracts URLs from messages.
"""

import re
from telethon import TelegramClient
from telethon.tl.types import Message
from typing import List, Dict
import config


class TelegramMonitor:
    """Monitor Telegram group for messages with URLs."""

    def __init__(self):
        self.client = TelegramClient(
            config.TELEGRAM_SESSION_FILE,
            config.TELEGRAM_API_ID,
            config.TELEGRAM_API_HASH
        )

    async def connect(self):
        """Connect to Telegram."""
        await self.client.start(phone=config.TELEGRAM_PHONE)
        print("✓ Connected to Telegram")

    async def get_messages_with_urls(self) -> List[Dict]:
        """
        Get recent messages from the configured chat and extract URLs.

        Returns:
            List of dicts with message_id, text, urls, date, sender
        """
        messages_with_urls = []

        try:
            # Get messages from the chat
            async for message in self.client.iter_messages(
                int(config.TELEGRAM_CHAT_ID),
                limit=config.MAX_MESSAGES_TO_PROCESS
            ):
                if isinstance(message, Message) and message.text:
                    # Extract URLs using regex
                    urls = self._extract_urls(message.text)

                    if urls:
                        messages_with_urls.append({
                            'message_id': message.id,
                            'text': message.text,
                            'urls': urls,
                            'date': message.date,
                            'sender_id': message.sender_id
                        })

            print(f"✓ Found {len(messages_with_urls)} messages with URLs")

        except Exception as e:
            print(f"✗ Error getting messages: {e}")
            raise

        return messages_with_urls

    def _extract_urls(self, text: str) -> List[str]:
        """Extract URLs from text using regex."""
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, text)
        return urls

    async def disconnect(self):
        """Disconnect from Telegram."""
        await self.client.disconnect()
        print("✓ Disconnected from Telegram")


async def get_urls_from_telegram() -> List[str]:
    """
    Main function to get URLs from Telegram.

    Returns:
        List of unique URLs found in recent messages
    """
    monitor = TelegramMonitor()

    try:
        await monitor.connect()
        messages = await monitor.get_messages_with_urls()

        # Extract all unique URLs
        all_urls = []
        for msg in messages:
            all_urls.extend(msg['urls'])

        # Remove duplicates and limit
        unique_urls = list(set(all_urls))[:config.MAX_URLS_TO_PROCESS]

        print(f"✓ Extracted {len(unique_urls)} unique URLs")
        return unique_urls

    finally:
        await monitor.disconnect()


if __name__ == '__main__':
    import asyncio

    # Test the monitor
    async def test():
        urls = await get_urls_from_telegram()
        print("\nURLs found:")
        for url in urls:
            print(f"  - {url}")

    asyncio.run(test())
