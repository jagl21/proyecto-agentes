"""
Main Agent Entry Point
Executes the content curation agent.
Supports both batch mode and real-time monitoring mode.
"""

import asyncio
from datetime import datetime
import config
from graph import create_agent_graph
from telegram_monitor import TelegramMonitor
import web_scraper
import content_processor
import image_handler
import api_client


def print_header():
    """Print agent header."""
    print("\n" + "="*60)
    print("  CONTENT CURATION AI AGENT")
    print("  Telegram → Web Scraping → AI Processing → Admin Review")
    print("="*60)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60 + "\n")


def print_summary(final_state):
    """Print execution summary."""
    print("\n" + "="*60)
    print("EXECUTION SUMMARY")
    print("="*60)

    processed = final_state.get('processed_posts', [])
    errors = final_state.get('errors', [])

    print(f"✓ Successfully processed: {len(processed)} posts")
    print(f"✗ Errors encountered: {len(errors)}")

    if processed:
        print("\nProcessed Posts:")
        for i, post in enumerate(processed, 1):
            print(f"  {i}. {post['title'][:60]}...")
            print(f"     URL: {post['url'][:70]}")
            print(f"     Post ID: {post.get('post_id', 'N/A')}")

    if errors:
        print("\nErrors:")
        for i, error in enumerate(errors, 1):
            print(f"  {i}. {error['url'][:70]}")
            print(f"     Stage: {error.get('stage', 'unknown')}")
            print(f"     Error: {error['error']}")

    print("\n" + "="*60)
    print("Next steps:")
    print("1. Open http://localhost:5000/admin.html")
    print("2. Review and approve pending posts")
    print("3. Published posts will appear on http://localhost:5000")
    print("="*60 + "\n")


async def main():
    """Main execution function."""
    try:
        # Validate configuration
        print("Checking configuration...")
        config.validate_config()

        # Print config
        config.print_config()

        # Print header
        print_header()

        # Create and run the agent graph
        print("Initializing agent graph...\n")
        agent = create_agent_graph()

        # Initial state
        initial_state = {
            'urls': [],
            'current_url_index': 0,
            'processed_posts': [],
            'errors': [],
            'stats': {}
        }

        # Execute the agent
        print("Starting agent execution...\n")
        final_state = await agent.ainvoke(
            initial_state,
            config={"recursion_limit": 100}
        )

        # Print summary
        print_summary(final_state)

        return final_state

    except KeyboardInterrupt:
        print("\n\n⚠ Agent execution interrupted by user")
        return None

    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main_realtime():
    """Main execution function for real-time monitoring mode."""
    try:
        # Validate configuration
        print("Checking configuration...")
        config.validate_config()

        # Print config
        config.print_config()

        # Print header for real-time mode
        print("\n" + "="*60)
        print("  CONTENT CURATION AI AGENT - REAL-TIME MODE")
        print("  Listening to Telegram for new messages...")
        print("="*60)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*60 + "\n")

        # Create Telegram monitor
        monitor = TelegramMonitor()
        await monitor.connect()

        # Define callback to process each URL
        async def process_single_url(url: str):
            """
            Process a single URL through the pipeline.
            This is called for each URL found in new Telegram messages.
            """
            print(f"\n{'='*70}")
            print(f"Processing URL: {url[:60]}...")
            print(f"{'='*70}")

            try:
                # Step 1: Scrape
                print("\n[1/4] Scraping URL...")
                scraped_data = await web_scraper.scrape_url(url)

                if not scraped_data['success']:
                    print(f"✗ Scraping failed: {scraped_data['error']}")
                    return

                print("✓ Scraping successful")

                # Step 2: Process content with AI
                print("\n[2/4] Processing content with AI...")
                processed_content = content_processor.process_scraped_content(scraped_data)

                if not processed_content['success']:
                    print(f"✗ Content processing failed: {processed_content['error']}")
                    return

                print(f"✓ Generated summary: {processed_content['title'][:50]}...")

                # Step 3: Handle image
                print("\n[3/4] Handling image...")
                image_url = image_handler.get_image_url(
                    scraped_data.get('image_url'),
                    processed_content['title'],
                    processed_content['summary']
                )

                if image_url:
                    print(f"✓ Image URL: {image_url[:60]}...")
                else:
                    print("⚠ No image available")

                # Step 4: Create pending post
                print("\n[4/4] Creating pending post...")
                result = api_client.create_pending_post(
                    title=processed_content['title'],
                    summary=processed_content['summary'],
                    source_url=url,
                    image_url=image_url,
                    provider=processed_content['provider'],
                    type=processed_content['type']
                )

                if result.get('success'):
                    post_id = result.get('data', {}).get('id')
                    print(f"✓ Pending post created successfully (ID: {post_id})")
                    print(f"   Title: {processed_content['title'][:60]}...")
                    print(f"   Review at: http://localhost:5000/admin")
                else:
                    print(f"✗ Failed to create post: {result.get('error')}")

            except Exception as e:
                print(f"\n✗ Error processing URL: {e}")
                import traceback
                traceback.print_exc()

        # Start real-time monitoring
        await monitor.start_realtime_monitoring(on_new_url=process_single_url)

    except KeyboardInterrupt:
        print("\n\n⚠ Agent stopped by user (Ctrl+C)")
        return None

    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    import sys

    # Check if real-time mode is requested
    if len(sys.argv) > 1 and sys.argv[1] == '--realtime':
        print("Starting in REAL-TIME mode...")
        result = asyncio.run(main_realtime())
    else:
        print("Starting in BATCH mode...")
        print("(Use --realtime flag for real-time monitoring)")
        result = asyncio.run(main())

    if result:
        print("✓ Agent execution completed successfully")
    else:
        print("✗ Agent execution failed or was interrupted")
