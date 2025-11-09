"""
Telegram Monitor Module
Connects to Telegram and extracts URLs from messages.
Supports both batch mode (process history) and real-time mode (listen for new messages).
"""

import re
from telethon import TelegramClient, events
from telethon.tl.types import Message
from typing import List, Dict, Callable, Awaitable
import config
from state_manager import StateManager
import asyncio


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

    async def start_realtime_monitoring(
        self,
        on_new_url: Callable[[str], Awaitable[None]]
    ):
        """
        Start real-time monitoring of Telegram chat for new messages.
        Listens indefinitely for new messages and processes URLs in real-time.

        Args:
            on_new_url: Async callback function to process each URL found
                        Function signature: async def callback(url: str) -> None
        """
        # Initialize state manager for deduplication
        state_manager = StateManager()

        print("\n" + "="*60)
        print("  REAL-TIME TELEGRAM MONITORING")
        print("="*60)
        print(f"Chat ID: {config.TELEGRAM_CHAT_ID}")
        print(f"Monitoring for new messages with URLs...")
        print("Press Ctrl+C to stop")
        print("="*60 + "\n")

        # Queue for processing URLs
        url_queue = asyncio.Queue()

        # Register event handler for new messages
        @self.client.on(events.NewMessage(chats=int(config.TELEGRAM_CHAT_ID)))
        async def handle_new_message(event):
            """Handle new messages from the configured chat."""
            message = event.message

            # Skip if already processed
            if state_manager.is_message_processed(message.id):
                print(f"⚠ Message {message.id} already processed (skipping)")
                return

            # Extract URLs from message
            if message.text:
                urls = self._extract_urls(message.text)

                if urls:
                    print(f"\n[{message.date.strftime('%H:%M:%S')}] New message with {len(urls)} URL(s)")

                    # Add URLs to processing queue
                    for url in urls:
                        await url_queue.put({
                            'message_id': message.id,
                            'url': url,
                            'date': message.date
                        })

        # Worker to process URLs from queue
        async def url_processor_worker():
            """Process URLs from the queue."""
            while True:
                try:
                    # Get URL from queue
                    url_data = await url_queue.get()

                    message_id = url_data['message_id']
                    url = url_data['url']

                    print(f"\n[Worker] Processing: {url[:70]}...")

                    try:
                        # Call the callback to process URL
                        await on_new_url(url)

                        # Mark as successfully processed
                        state_manager.mark_message_processed(
                            message_id=message_id,
                            chat_id=config.TELEGRAM_CHAT_ID,
                            url=url,
                            status='processed'
                        )

                        print(f"✓ Completed processing: {url[:70]}")

                    except Exception as e:
                        # Mark as failed
                        state_manager.mark_message_processed(
                            message_id=message_id,
                            chat_id=config.TELEGRAM_CHAT_ID,
                            url=url,
                            status='failed',
                            error=str(e)
                        )

                        print(f"✗ Error processing URL: {e}")

                    finally:
                        url_queue.task_done()

                except Exception as e:
                    print(f"✗ Worker error: {e}")

        # Start worker task
        worker_task = asyncio.create_task(url_processor_worker())

        try:
            # Keep client running and listening for events
            print("✓ Event handlers registered")
            print("✓ Worker started")
            print("\nListening for new messages...\n")

            await self.client.run_until_disconnected()

        except KeyboardInterrupt:
            print("\n\n⚠ Monitoring stopped by user (Ctrl+C)")
            worker_task.cancel()

        except Exception as e:
            print(f"\n✗ Fatal error in monitoring: {e}")
            worker_task.cancel()
            raise

        finally:
            # Print final stats
            stats = state_manager.get_stats()
            print("\n" + "="*60)
            print("MONITORING SESSION STATS")
            print("="*60)
            print(f"Total messages processed: {stats['total']}")
            print(f"Successful: {stats['processed']}")
            print(f"Failed: {stats['failed']}")
            print(f"Skipped: {stats['skipped']}")
            print("="*60 + "\n")


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
