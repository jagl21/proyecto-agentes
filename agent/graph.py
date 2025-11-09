"""
LangGraph Agent Definition
Orchestrates the content curation workflow for a single URL.
"""

from typing import TypedDict, Optional
from langgraph.graph import StateGraph, END

import web_scraper
import content_processor
import image_handler
import api_client


# Define the state structure for processing a single URL
class AgentState(TypedDict, total=False):
    """State for processing a single URL through the content curation pipeline.

    Using total=False makes all fields optional, allowing partial state updates.
    LangGraph will merge updates from nodes using the specified reducers.
    """
    # Input
    url: str  # The URL to process

    # Pipeline fields
    scraped_data: dict  # Data extracted from web scraping
    processed_content: dict  # Content processed by AI
    final_image_url: str  # Final image URL (validated or generated)

    # Output
    success: bool  # Whether the URL was processed successfully
    error: Optional[str]  # Error message if processing failed
    error_stage: Optional[str]  # Stage where error occurred
    post_id: Optional[int]  # ID of created pending post (if successful)


# Node functions
async def scrape_url_node(state: AgentState) -> dict:
    """Node: Scrape the URL."""
    url = state['url']
    print(f"\n[1/4] Scraping URL: {url[:70]}...")

    scraped_data = await web_scraper.scrape_url(url)

    if scraped_data['success']:
        print(f"✓ Scraping successful")
        return {
            'scraped_data': scraped_data,
            'success': True
        }
    else:
        print(f"✗ Scraping failed: {scraped_data['error']}")
        return {
            'success': False,
            'error': scraped_data['error'],
            'error_stage': 'scraping'
        }


def process_content_node(state: AgentState) -> dict:
    """Node: Process content with AI."""
    # If scraping failed, skip this node
    if not state.get('success', True):
        return {}

    print("[2/4] Processing content with AI...")

    try:
        processed = content_processor.process_scraped_content(state['scraped_data'])

        if processed['success']:
            print(f"✓ AI processing successful: {processed['title'][:50]}...")
            return {'processed_content': processed}
        else:
            print(f"✗ Content processing failed")
            return {
                'success': False,
                'error': 'Content processing failed',
                'error_stage': 'ai_processing'
            }

    except Exception as e:
        print(f"✗ Exception in content processing: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_stage': 'ai_processing'
        }


def handle_image_node(state: AgentState) -> dict:
    """Node: Handle image (validate or generate)."""
    # If previous step failed, skip this node
    if not state.get('success', True):
        return {}

    print("[3/4] Handling image...")

    try:
        scraped_data = state['scraped_data']
        processed = state['processed_content']

        image_url = image_handler.handle_image(
            scraped_data.get('image_url'),
            processed['title'],
            processed['summary']
        )

        if image_url:
            print(f"✓ Image handled: {image_url[:70]}...")
        else:
            print(f"⚠ No image available")

        return {'final_image_url': image_url}

    except Exception as e:
        print(f"✗ Exception in image handling: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_stage': 'image_handling'
        }


def create_pending_post_node(state: AgentState) -> dict:
    """Node: Create pending post via API."""
    # If previous step failed, skip this node
    if not state.get('success', True):
        return {}

    print("[4/4] Creating pending post...")

    try:
        processed = state['processed_content']
        scraped_data = state['scraped_data']

        result = api_client.create_pending_post(
            title=processed['title'],
            summary=processed['summary'],
            source_url=state['url'],
            image_url=state.get('final_image_url'),
            provider=processed['provider'],
            type=processed['type']
        )

        if result.get('success'):
            post_id = result.get('data', {}).get('id')
            print(f"✓ Post created successfully (ID: {post_id})")
            print(f"   Title: {processed['title'][:60]}...")
            return {
                'success': True,
                'post_id': post_id
            }
        else:
            error_msg = result.get('error', 'Unknown API error')
            print(f"✗ Failed to create post: {error_msg}")
            return {
                'success': False,
                'error': error_msg,
                'error_stage': 'api_creation'
            }

    except Exception as e:
        print(f"✗ Exception creating pending post: {e}")
        return {
            'success': False,
            'error': str(e),
            'error_stage': 'api_creation'
        }


def create_agent_graph():
    """Create and compile the LangGraph agent for processing a single URL."""
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("scrape_url", scrape_url_node)
    workflow.add_node("process_content", process_content_node)
    workflow.add_node("handle_image", handle_image_node)
    workflow.add_node("create_pending_post", create_pending_post_node)

    # Define linear pipeline (no loops, single URL processing)
    workflow.set_entry_point("scrape_url")
    workflow.add_edge("scrape_url", "process_content")
    workflow.add_edge("process_content", "handle_image")
    workflow.add_edge("handle_image", "create_pending_post")
    workflow.add_edge("create_pending_post", END)

    # Compile
    return workflow.compile()


if __name__ == '__main__':
    print("LangGraph agent definition loaded successfully")
    print("This graph processes a single URL through the pipeline:")
    print("  scrape_url → process_content → handle_image → create_pending_post")
