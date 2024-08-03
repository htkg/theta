import os
import json
from dataclasses import dataclass, field
from datetime import datetime, UTC
from typing import List, Optional, Dict, Any

import httpx
import http.cookiejar


@dataclass(frozen=True)
class Media:
    """Represents an Instagram media post."""
    id: str
    source: str
    attachments: List[Dict[str, Any]]
    retrieved_at: datetime
    published_at: datetime
    source_url: Optional[str] = None
    tags: Optional[List[str]] = field(default_factory=list)
    title: Optional[str] = None
    author_id: Optional[str] = None
    author_name: Optional[str] = None
    author_url: Optional[str] = None
    description: Optional[str] = None
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None


class InstagramMediaFetcher:
    """A class for fetching Instagram media data."""

    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR = os.path.join(BASE_DIR, 'config')
    # Exported using Fiddler
    HEADERS_FILE = os.path.join(CONFIG_DIR, 'headers.txt')
    # Should be exported with Netscape format from your browser (Firefox most popular extension was used). This is required as Instagram limited anonymous usage and it's now requires authenication to fetch media data.
    COOKIES_FILE = os.path.join(CONFIG_DIR, 'cookies.txt')
    # Exported using Fiddler
    PAYLOAD_FILE = os.path.join(CONFIG_DIR, 'payload.txt')
    API_URL = "https://www.instagram.com/graphql/query"

    def __init__(self) -> None:
        """Initialize the InstagramMediaFetcher with headers, cookies, and payload."""
        self.headers = self._get_headers()
        self.cookie_jar = self._get_cookiejar()
        self.payload = self._get_payload()

    def _get_headers(self) -> Dict[str, str]:
        """
        Load headers from a file.

        Returns:
            Dict[str, str]: A dictionary of HTTP headers.
        """
        with open(self.HEADERS_FILE, 'r', encoding='utf-8') as f:
            return {
                key: value.strip()
                for line in f
                if ': ' in line
                for key, value in [line.split(': ', 1)]
            }

    def _get_cookiejar(self) -> http.cookiejar.MozillaCookieJar:
        """
        Load cookies from a file to authenticate user.

        Returns:
            http.cookiejar.MozillaCookieJar: A cookie jar object.
        """
        cookie_jar = http.cookiejar.MozillaCookieJar(self.COOKIES_FILE)
        cookie_jar.load(ignore_discard=True, ignore_expires=True)
        return cookie_jar

    def _get_payload(self) -> Dict[str, Any]:
        """
        Load payload from a file.

        Returns:
            Dict[str, Any]: A dictionary containing the payload data.
        """
        with open(self.PAYLOAD_FILE, 'r', encoding='utf-8') as f:
            payload = {}
            for line in f:
                key, value = line.strip().split('\t')
                payload[key] = json.loads(value) if key == 'variables' else value
        return payload

    @staticmethod
    def _get_tags_from_caption(caption: Optional[str]) -> List[str]:
        """
        Extract hashtags from the caption.

        Args:
            caption (Optional[str]): The caption text.

        Returns:
            List[str]: A list of hashtags.
        """
        return caption.split(' #')[1:] if caption else []

    def _parse_media_json(self, media_data: Dict[str, Any]) -> Media:
        """
        Parse media JSON data into a Media object.

        Args:
            media_data (Dict[str, Any]): The raw JSON data of the media.

        Returns:
            Media: A Media object containing the parsed data.
        """
        media = media_data.get("data", {}).get("xdt_api__v1__media__shortcode__web_info", {}).get("items", [])[0]

        owner = media.get("owner", {})
        caption = media.get('caption', {})

        return Media(
            id=media.get("code"),
            source="Instagram",
            attachments=media.get('video_versions', []) or [media.get('image_versions2')] if media.get(
                'image_versions2') else [],
            retrieved_at=datetime.now(UTC),
            published_at=datetime.fromtimestamp(media.get("taken_at", 0), UTC),
            source_url=f"https://www.instagram.com/p/{media.get('code')}",
            tags=self._get_tags_from_caption(caption.get('text')),
            author_id=owner.get("id"),
            author_name=owner.get("username"),
            author_url=f"https://www.instagram.com/{owner.get('username', '')}",
            description=caption.get('text'),
            views=media.get("view_count"),
            likes=media.get("like_count"),
            title=media.get("title"),
            comments=media.get("comment_count")
        )

    def get_instagram_media(self, media_id: str) -> Media:
        """
        Fetch Instagram media data.

        Args:
            media_id (str): The ID of the Instagram media to fetch.

        Returns:
            Media: A Media object containing the fetched data.

        Raises:
            ValueError: If an HTTP error occurs, the JSON response is invalid,
                        or if there's a missing key in the response.
        """
        self.payload["variables"]["shortcode"] = media_id

        try:
            with httpx.Client(headers=self.headers, cookies=self.cookie_jar) as client:
                response = client.post(self.API_URL, json=self.payload)
                response.raise_for_status()
                media = self._parse_media_json(response.json())
            return media
        except httpx.HTTPStatusError as e:
            raise ValueError(f"HTTP error occurred: {e}")
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON response")
        except KeyError as e:
            raise ValueError(f"Missing key in response: {e}")