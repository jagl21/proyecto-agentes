"""
LangGraph Agent Definition
Orchestrates the content curation workflow.
"""

from typing import TypedDict, List, Annotated, Optional
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime

import telegram_monitor
import web_scraper
import content_processor
import image_handler
import api_client


# Define the state structure
class AgentState(TypedDict, total=False):
    """State for the content curation agent.

    Using total=False makes all fields optional, allowing partial state updates.
    LangGraph will merge updates from nodes using the specified reducers.
    """
    # Core workflow fields (always initialized)
    urls: List[str]
    current_url_index: int
    processed_posts: Annotated[List[dict], operator.add]  # Accumulates successfully processed posts
    errors: Annotated[List[dict], operator.add]  # Accumulates errors encountered
    stats: dict

    # Temporary fields (used between nodes during URL processing loop)
    scraped_data: dict  # Data extracted from web scraping
    processed_content: dict  # Content processed by AI
    final_image_url: str  # Final image URL (validated or generated)
    skip_processing: bool  # Flag to skip remaining nodes for current URL


# Node functions
async def monitor_telegram_node(state: AgentState) -> dict:
    """Node: Get URLs from Telegram."""
    print("\n[1/5] Monitoring Telegram for URLs...")

    urls = await telegram_monitor.get_urls_from_telegram()

    print(f"✓ Found {len(urls)} URLs to process\n")

    return {
        'urls': urls,
        'current_url_index': 0
    }


async def scrape_url_node(state: AgentState) -> dict:
    """Node: Scrape current URL."""
    idx = state['current_url_index']
    urls = state['urls']

    if idx >= len(urls):
        return {'skip_processing': True}

    url = urls[idx]
    print(f"\n[2/5] Scraping URL {idx + 1}/{len(urls)}: {url[:60]}...")

    scraped_data = await web_scraper.scrape_url(url)

    if scraped_data['success']:
        return {
            'scraped_data': scraped_data,
            'skip_processing': False
        }
    else:
        return {
            'errors': [{
                'url': url,
                'error': scraped_data['error'],
                'stage': 'scraping'
            }],
            'skip_processing': True
        }


def process_content_node(state: AgentState) -> dict:
    """Node: Process content with AI."""
    skip = state.get('skip_processing', False)
    has_data = 'scraped_data' in state

    if skip or not has_data:
        print(f"⚠ Skipping processing - skip_processing: {skip}, has_scraped_data: {has_data}")
        return {}

    print("[3/5] Processing content with AI...")

    try:
        processed = content_processor.process_scraped_content(state['scraped_data'])

        if processed['success']:
            return {'processed_content': processed}
        else:
            print(f"✗ Content processing failed")
            return {
                'errors': [{
                    'url': state['scraped_data'].get('url', 'unknown'),
                    'error': 'Content processing failed',
                    'stage': 'processing'
                }],
                'skip_processing': True
            }

    except Exception as e:
        print(f"✗ Exception in content processing: {e}")
        return {
            'errors': [{
                'url': state['scraped_data'].get('url', 'unknown'),
                'error': str(e),
                'stage': 'processing'
            }],
            'skip_processing': True
        }


def handle_image_node(state: AgentState) -> dict:
    """Node: Handle image (validate or generate)."""
    skip = state.get('skip_processing', False)
    has_content = 'processed_content' in state

    if skip or not has_content:
        print(f"⚠ Skipping image handling - skip_processing: {skip}, has_processed_content: {has_content}")
        return {}

    print("[4/5] Handling image...")

    try:
        scraped_data = state['scraped_data']
        processed = state['processed_content']

        image_url = image_handler.handle_image(
            scraped_data.get('image_url'),
            processed['title'],
            processed['summary']
        )

        print(f"✓ Image handled: {image_url[:80] if image_url else 'None'}...")
        return {'final_image_url': image_url}

    except Exception as e:
        print(f"✗ Exception in image handling: {e}")
        return {
            'errors': [{
                'url': state['scraped_data'].get('url', 'unknown'),
                'error': str(e),
                'stage': 'image_handling'
            }],
            'skip_processing': True
        }


def create_pending_post_node(state: AgentState) -> dict:
    """Node: Create pending post via API."""
    skip = state.get('skip_processing', False)
    has_content = 'processed_content' in state

    # Prepare the base update (always increment index)
    update = {
        'current_url_index': state['current_url_index'] + 1
    }

    if not skip and has_content:
        print("[5/5] Creating pending post...")

        try:
            processed = state['processed_content']
            scraped_data = state['scraped_data']

            result = api_client.create_pending_post(
                title=processed['title'],
                summary=processed['summary'],
                source_url=scraped_data['url'],
                image_url=state.get('final_image_url'),
                provider=processed['provider'],
                type=processed['type']
            )

            if result.get('success'):
                update['processed_posts'] = [{
                    'url': scraped_data['url'],
                    'title': processed['title'],
                    'post_id': result.get('data', {}).get('id')
                }]
                print(f"✓ Post created successfully: {processed['title'][:60]}...")
            else:
                error_msg = result.get('error', 'Unknown API error')
                print(f"✗ Failed to create post: {error_msg}")
                update['errors'] = [{
                    'url': scraped_data['url'],
                    'error': error_msg,
                    'stage': 'api_post_creation'
                }]

        except Exception as e:
            print(f"✗ Exception creating pending post: {e}")
            update['errors'] = [{
                'url': state.get('scraped_data', {}).get('url', 'unknown'),
                'error': str(e),
                'stage': 'api_post_creation'
            }]
    else:
        print(f"⚠ Skipping post creation - skip_processing: {skip}, has_processed_content: {has_content}")

    return update


def should_continue(state: AgentState) -> str:
    """Decide if we should process more URLs."""
    if state['current_url_index'] < len(state['urls']):
        return "continue"
    else:
        return "end"


def create_agent_graph():
    """Create and compile the LangGraph agent."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("monitor_telegram", monitor_telegram_node)
    workflow.add_node("scrape_url", scrape_url_node)
    workflow.add_node("process_content", process_content_node)
    workflow.add_node("handle_image", handle_image_node)
    workflow.add_node("create_pending_post", create_pending_post_node)

    # Define edges
    workflow.set_entry_point("monitor_telegram")
    workflow.add_edge("monitor_telegram", "scrape_url")
    workflow.add_edge("scrape_url", "process_content")
    workflow.add_edge("process_content", "handle_image")
    workflow.add_edge("handle_image", "create_pending_post")

    # Conditional edge: loop or end
    workflow.add_conditional_edges(
        "create_pending_post",
        should_continue,
        {
            "continue": "scrape_url",
            "end": END
        }
    )

    # Compile with increased recursion limit
    return workflow.compile(
        checkpointer=None,
        interrupt_before=None,
        interrupt_after=None,
        debug=False
    )


if __name__ == '__main__':
    print("LangGraph agent definition loaded successfully")
