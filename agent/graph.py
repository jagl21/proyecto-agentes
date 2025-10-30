"""
LangGraph Agent Definition
Orchestrates the content curation workflow.
"""

from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, END
import operator
from datetime import datetime

import telegram_monitor
import web_scraper
import content_processor
import image_handler
import api_client


# Define the state structure
class AgentState(TypedDict):
    """State for the content curation agent."""
    urls: List[str]
    current_url_index: int
    processed_posts: List[dict]
    errors: List[dict]
    stats: dict


# Node functions
async def monitor_telegram_node(state: AgentState) -> AgentState:
    """Node: Get URLs from Telegram."""
    print("\n[1/5] Monitoring Telegram for URLs...")

    urls = await telegram_monitor.get_urls_from_telegram()

    state['urls'] = urls
    state['current_url_index'] = 0
    state['processed_posts'] = []
    state['errors'] = []

    print(f"✓ Found {len(urls)} URLs to process\n")
    return state


async def scrape_url_node(state: AgentState) -> AgentState:
    """Node: Scrape current URL."""
    idx = state['current_url_index']
    urls = state['urls']

    if idx >= len(urls):
        return state

    url = urls[idx]
    print(f"\n[2/5] Scraping URL {idx + 1}/{len(urls)}: {url[:60]}...")

    scraped_data = await web_scraper.scrape_url(url)

    if scraped_data['success']:
        state['scraped_data'] = scraped_data
    else:
        state['errors'].append({
            'url': url,
            'error': scraped_data['error'],
            'stage': 'scraping'
        })

    return state


def process_content_node(state: AgentState) -> AgentState:
    """Node: Process content with AI."""
    if 'scraped_data' not in state:
        return state

    print("[3/5] Processing content with AI...")

    processed = content_processor.process_scraped_content(state['scraped_data'])

    if processed['success']:
        state['processed_content'] = processed

    return state


def handle_image_node(state: AgentState) -> AgentState:
    """Node: Handle image (validate or generate)."""
    if 'processed_content' not in state:
        return state

    print("[4/5] Handling image...")

    scraped_data = state['scraped_data']
    processed = state['processed_content']

    image_url = image_handler.handle_image(
        scraped_data.get('image_url'),
        processed['title'],
        processed['summary']
    )

    state['final_image_url'] = image_url
    return state


def create_pending_post_node(state: AgentState) -> AgentState:
    """Node: Create pending post via API."""
    if 'processed_content' not in state:
        return state

    print("[5/5] Creating pending post...")

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
        state['processed_posts'].append({
            'url': scraped_data['url'],
            'title': processed['title'],
            'post_id': result.get('data', {}).get('id')
        })

    # Cleanup temporary state
    if 'scraped_data' in state:
        del state['scraped_data']
    if 'processed_content' in state:
        del state['processed_content']
    if 'final_image_url' in state:
        del state['final_image_url']

    # Move to next URL
    state['current_url_index'] += 1

    return state


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

    return workflow.compile()


if __name__ == '__main__':
    print("LangGraph agent definition loaded successfully")
