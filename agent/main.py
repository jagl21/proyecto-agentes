"""
Main Agent Entry Point
Executes the content curation agent.
Supports both real-time (default) and batch modes, both using LangGraph.
"""

import asyncio
from datetime import datetime
import config
from graph import create_agent_graph
from telegram_monitor import TelegramMonitor
from state_manager import StateManager


def print_header(mode: str):
    """Print agent header."""
    mode_display = "REAL-TIME MONITORING" if mode == "realtime" else "BATCH PROCESSING"
    print("\n" + "="*70)
    print(f"  CONTENT CURATION AI AGENT - {mode_display}")
    print("  Telegram → Web Scraping → AI Processing → Admin Review")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if mode == "realtime":
        print("Listening for new messages... (Press Ctrl+C to stop)")
    print("="*70 + "\n")


async def process_url_with_graph(agent, url: str) -> dict:
    """
    Process a single URL through the LangGraph pipeline.

    Args:
        agent: Compiled LangGraph agent
        url: URL to process

    Returns:
        Result dict with success status and details
    """
    try:
        # Invoke the graph with a single URL
        result = await agent.ainvoke({'url': url})
        return result

    except Exception as e:
        print(f"✗ Exception processing {url}: {e}")
        return {
            'url': url,
            'success': False,
            'error': str(e),
            'error_stage': 'graph_execution'
        }


async def main_realtime():
    """
    Real-time monitoring mode (DEFAULT).
    Listens continuously for new Telegram messages and processes URLs using LangGraph.
    """
    try:
        # Validate configuration
        print("Checking configuration...")
        config.validate_config()
        config.print_config()

        print_header("realtime")

        # Create LangGraph agent
        print("Initializing LangGraph agent...\n")
        agent = create_agent_graph()

        # Create Telegram monitor and state manager
        monitor = TelegramMonitor()
        state_manager = StateManager()
        await monitor.connect()

        # Statistics
        stats = {'processed': 0, 'failed': 0, 'skipped': 0}

        # Define callback to process each URL with LangGraph
        async def process_single_url(url: str):
            """Process a single URL through the LangGraph pipeline."""
            nonlocal stats

            print(f"\n{'='*70}")
            print(f"Processing URL: {url[:60]}...")
            print(f"{'='*70}")

            try:
                # Invoke LangGraph for this URL
                result = await process_url_with_graph(agent, url)

                if result.get('success'):
                    stats['processed'] += 1
                    print(f"\n✓ URL processed successfully")
                    print(f"   Review at: http://localhost:5000/admin")
                else:
                    stats['failed'] += 1
                    print(f"\n✗ URL processing failed: {result.get('error')}")

            except Exception as e:
                stats['failed'] += 1
                print(f"\n✗ Error processing URL: {e}")
                import traceback
                traceback.print_exc()

        # Start real-time monitoring
        await monitor.start_realtime_monitoring(on_new_url=process_single_url)

    except KeyboardInterrupt:
        print("\n\n⚠ Agent stopped by user (Ctrl+C)")
        print(f"\nSession stats: {stats['processed']} processed, {stats['failed']} failed")
        return None

    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main_batch():
    """
    Batch processing mode.
    Processes historical messages from Telegram using LangGraph.
    """
    try:
        # Validate configuration
        print("Checking configuration...")
        config.validate_config()
        config.print_config()

        print_header("batch")

        # Create LangGraph agent
        print("Initializing LangGraph agent...\n")
        agent = create_agent_graph()

        # Get URLs from Telegram history
        print("Fetching messages from Telegram...\n")
        monitor = TelegramMonitor()
        await monitor.connect()

        messages = await monitor.get_messages_with_urls()
        await monitor.disconnect()

        # Extract all unique URLs
        all_urls = []
        for msg in messages:
            all_urls.extend(msg['urls'])

        unique_urls = list(set(all_urls))[:config.MAX_URLS_TO_PROCESS]
        print(f"✓ Found {len(unique_urls)} unique URLs to process\n")

        # Statistics
        processed = 0
        failed = 0

        # Process each URL with LangGraph
        for i, url in enumerate(unique_urls, 1):
            print(f"\n{'='*70}")
            print(f"[{i}/{len(unique_urls)}] Processing: {url[:60]}...")
            print(f"{'='*70}")

            result = await process_url_with_graph(agent, url)

            if result.get('success'):
                processed += 1
                print(f"✓ URL {i}/{len(unique_urls)} processed successfully")
            else:
                failed += 1
                print(f"✗ URL {i}/{len(unique_urls)} failed: {result.get('error')}")

        # Print summary
        print("\n" + "="*70)
        print("BATCH PROCESSING SUMMARY")
        print("="*70)
        print(f"✓ Successfully processed: {processed} URLs")
        print(f"✗ Failed: {failed} URLs")
        print("\nNext steps:")
        print("1. Open http://localhost:5000/admin.html")
        print("2. Review and approve pending posts")
        print("3. Published posts will appear on http://localhost:5000")
        print("="*70 + "\n")

        return {'processed': processed, 'failed': failed}

    except KeyboardInterrupt:
        print("\n\n⚠ Batch processing interrupted by user")
        return None

    except Exception as e:
        print(f"\n\n✗ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == '__main__':
    import sys

    # Check if batch mode is requested (otherwise default to real-time)
    if len(sys.argv) > 1 and sys.argv[1] == '--batch':
        print("Starting in BATCH mode (historical messages)...")
        result = asyncio.run(main_batch())
    else:
        print("Starting in REAL-TIME mode (continuous monitoring)...")
        print("(Use --batch flag for batch processing of historical messages)\n")
        result = asyncio.run(main_realtime())

    if result:
        print("\n✓ Agent execution completed successfully")
    else:
        print("\n✗ Agent execution failed or was interrupted")
