import os
import requests
import xml.etree.ElementTree as ET
from agents import function_tool

# Default RSS feed URLs (can be overridden via environment variables)
DEFAULT_BLOG_RSS_URL = os.getenv("BLOG_RSS_URL", "https://blogs.justenougharchitecture.com/feed/")
DEFAULT_PODCAST_RSS_URL = os.getenv("PODCAST_RSS_URL", "https://anchor.fm/s/ef71d80c/podcast/rss")

@function_tool
def get_blog_rss_feed(rss_url: str = DEFAULT_BLOG_RSS_URL):
    """
    Retrieve and analyze blog RSS feeds.
    Fetches the latest blog posts from an RSS feed.

    Be conversational and helpful in your responses.
    """
    return _get_rss_feed(rss_url, "blog", "posts", "latest_posts")


@function_tool
def get_podcast_rss_feed(podcast_rss_url: str = DEFAULT_PODCAST_RSS_URL):
    """
    Retrieve and analyze podcast RSS feeds.
    Fetches the latest podcast episodes from an RSS feed.

    Be conversational and helpful in your responses.
    """
    return _get_rss_feed(podcast_rss_url, "podcast", "episodes", "latest_episodes")


def _get_rss_feed(feed_url: str, feed_type: str, item_name: str, items_key: str):
    """
    Generic RSS feed parser for both blogs and podcasts.

    Args:
        feed_url: The RSS feed URL to fetch
        feed_type: Type of feed ("blog" or "podcast")
        item_name: Name for counting items ("posts" or "episodes")
        items_key: Key name in result dict ("latest_posts" or "latest_episodes")
    """
    try:
        response = requests.get(feed_url, timeout=10)
        response.raise_for_status()

        # Parse the RSS XML
        root = ET.fromstring(response.content)

        items = []

        # Look for items in the RSS feed
        feed_items = root.findall('.//item') or root.findall('.//entry')

        for item in feed_items[:5]:  # Limit to 5 most recent items
            parsed_item = {}

            # Extract title
            title_elem = item.find('title') or item.find('.//title')
            if title_elem is not None and title_elem.text:
                parsed_item['title'] = title_elem.text.strip()

            # Extract link
            link_elem = item.find('link') or item.find('.//link')
            if link_elem is not None and link_elem.text:
                parsed_item['link'] = link_elem.text.strip()

            # Extract description/summary
            desc_elem = item.find('description') or item.find('.//summary') or item.find('.//content')
            if desc_elem is not None and desc_elem.text:
                parsed_item['description'] = desc_elem.text.strip()

            # Extract publication date
            date_elem = item.find('pubDate') or item.find('.//published') or item.find('.//updated')
            if date_elem is not None and date_elem.text:
                parsed_item['published'] = date_elem.text.strip()

            # Podcast-specific fields
            if feed_type == "podcast":
                # Extract duration
                duration_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}duration')
                if duration_elem is not None and duration_elem.text:
                    parsed_item['duration'] = duration_elem.text.strip()

                # Extract episode number
                episode_elem = item.find('.//{http://www.itunes.com/dtds/podcast-1.0.dtd}episode')
                if episode_elem is not None and episode_elem.text:
                    parsed_item['episode_number'] = episode_elem.text.strip()

            # Only add items that have at least a title
            if parsed_item.get('title'):
                items.append(parsed_item)

        if items:
            url_key = f"{feed_type}_rss_url" if feed_type == "podcast" else "rss_url"
            return {
                "status": "success",
                url_key: feed_url,
                f"{item_name}_found": len(items),
                items_key: items
            }
        else:
            url_key = f"{feed_type}_rss_url" if feed_type == "podcast" else "rss_url"
            return {
                "status": "success",
                url_key: feed_url,
                f"{item_name}_found": 0,
                "message": f"No {item_name} found in RSS feed"
            }

    except requests.RequestException as e:
        url_key = f"{feed_type}_rss_url" if feed_type == "podcast" else "rss_url"
        return {
            "status": "error",
            url_key: feed_url,
            "error": f"Failed to fetch RSS feed: {str(e)}"
        }
    except ET.ParseError as e:
        url_key = f"{feed_type}_rss_url" if feed_type == "podcast" else "rss_url"
        return {
            "status": "error",
            url_key: feed_url,
            "error": f"Failed to parse RSS feed: {str(e)}"
        }
    except Exception as e:
        url_key = f"{feed_type}_rss_url" if feed_type == "podcast" else "rss_url"
        return {
            "status": "error",
            url_key: feed_url,
            "error": f"Unexpected error: {str(e)}"
        }
