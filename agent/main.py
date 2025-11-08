"""
Main Agent Entry Point
Executes the content curation agent.
"""

import asyncio
from datetime import datetime
import config
from graph import create_agent_graph


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


if __name__ == '__main__':
    # Run the agent
    result = asyncio.run(main())

    if result:
        print("✓ Agent execution completed successfully")
    else:
        print("✗ Agent execution failed or was interrupted")
