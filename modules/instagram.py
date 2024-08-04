import http.cookiejar
import json
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any

import httpx
from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from structlog import get_logger

logger = get_logger('instagram')

@dataclass(frozen=True)
class Media:
    """Represents an Instagram media post."""
    id: str
    source: str
    attachments: List[str]
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

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    CONFIG_DIR: str = os.path.join(BASE_DIR, 'config')
    HEADERS_FILE: str = os.path.join(CONFIG_DIR, 'headers.txt')
    COOKIES_FILE: str = os.path.join(CONFIG_DIR, 'cookies.txt')
    PAYLOAD_FILE: str = os.path.join(CONFIG_DIR, 'payload.txt')
    API_URL: str = "https://www.instagram.com/graphql/query"

    def __init__(self) -> None:
        """Initialize the InstagramMediaFetcher with headers, cookies, and payload."""
        self.headers: Dict[str, str] = self._get_headers()
        self.cookie_jar: http.cookiejar.MozillaCookieJar = self._get_cookiejar()
        self.payload: Dict[str, Any] = self._get_payload()

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
        Load cookies from a file to authenticate the user.

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
    def get_shortcode_from_url(url: str) -> str:
        """
        Extracts the shortcode from a URL.

        Args:
            url (str): The URL to extract the shortcode from.

        Returns:
            str: The extracted shortcode.

        Raises:
            HTTPException: If the URL is invalid.
        """
        pattern = r"(?:https?://)?(?:www\.)?instagram\.com/.+?/([a-zA-Z0-9-_]+)(?:/.*)?"
        match = re.search(pattern, url)

        if not match:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="Invalid URL")
        return match.group(1)

    @staticmethod
    def _get_tags_from_caption(caption: Optional[str]) -> List[str]:
        """
        Extract hashtags from the caption.

        Args:
            caption (Optional[str]): The caption text.

        Returns:
            List[str]: A list of hashtags.
        """
        if not caption:
            return []
        return caption.split(' #')[1:] if caption else []

    @staticmethod
    def extract_max_resolutions(candidates: List[Dict[str, Any]]) -> Optional[str]:
        """
        Extract the URL of the highest resolution media from candidates.

        Args:
            candidates (List[Dict[str, Any]]): List of media candidates.

        Returns:
            Optional[str]: URL of the highest resolution media or None.
        """
        if not candidates:
            return None
        try:
            max_resolution = max(candidates, key=lambda x: x['width'] * x['height'])
            return max_resolution['url']
        except (KeyError, TypeError) as e:
            logger.error("An error occurred while extracting max resolutions: %s", e)
            return None

    def get_best_resolution(self, item: Dict[str, Any]) -> Optional[str]:
        """
        Get the best resolution media URL from an item.

        Args:
            item (Dict[str, Any]): A dictionary containing media item information.

        Returns:
            Optional[str]: URL of the best resolution media or None.
        """
        if 'video_versions' in item and item['video_versions']:
            video_versions = item.get('video_versions', [])
            return self.extract_max_resolutions(video_versions)

        if 'image_versions2' in item:
            image_versions = item.get('image_versions2', {}).get('candidates', [])
            return self.extract_max_resolutions(image_versions)

        return None

    def extract_candidates(self, media: Dict[str, Any]) -> List[Optional[str]]:
        """
        Extract candidates for the best resolution media URLs.

        Args:
            media (Dict[str, Any]): A dictionary containing media information.

        Returns:
            List[Optional[str]]: A list of the best resolution media URLs.
        """
        candidates = []

        if 'carousel_media' in media and media['carousel_media']:
            for carousel_item in media['carousel_media']:
                best_resolution = self.get_best_resolution(carousel_item)
                if best_resolution:
                    candidates.append(best_resolution)
        else:
            best_resolution = self.get_best_resolution(media)
            if best_resolution:
                candidates.append(best_resolution)

        return candidates

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
        caption = media.get('caption')
        caption_text = caption.get('text') if isinstance(caption, dict) else None

        return Media(
            id=media.get("code"),
            source="Instagram",
            attachments=self.extract_candidates(media),
            published_at=datetime.fromtimestamp(media.get("taken_at", 0), timezone.utc),
            source_url=f"https://www.instagram.com/p/{media.get('code')}",
            tags=self._get_tags_from_caption(caption_text),
            author_id=owner.get("id"),
            author_name=owner.get("username"),
            author_url=f"https://www.instagram.com/{owner.get('username', '')}",
            description=caption_text,
            views=media.get("view_count"),
            likes=media.get("like_count"),
            title=media.get("title"),
            comments=media.get("comment_count")
        )

    async def get_instagram_media(self, media_id: str) -> Media:
        """
        Fetch Instagram media data.

        Args:
            media_id (str): The ID of the Instagram media to fetch.

        Returns:
            Media: A Media object containing the fetched data.

        Raises:
            HTTPException: If the media_id is invalid, an HTTP error occurs,
                           the JSON response is invalid, or if there's a missing key in the response.
        """
        media_id_pattern = r'^[A-Za-z0-9_-]{7,39}$'
        if not re.match(media_id_pattern, media_id):
            raise HTTPException(
                status_code=HTTP_400_BAD_REQUEST,
                detail="Invalid media_id format. It should be 7-14 characters long and contain only letters, numbers, underscores, or hyphens.",
                extra={"media_id": media_id}
            )

        self.payload["variables"]["shortcode"] = media_id

        logger.info(f"Fetching Instagram media with id '{media_id}'")

        async with httpx.AsyncClient(headers=self.headers, cookies=self.cookie_jar) as client:
            response = await client.post(self.API_URL, json=self.payload)
            response.raise_for_status()
            json_data = response.json()

        items = json_data.get("data", {}).get("xdt_api__v1__media__shortcode__web_info", {}).get("items")
        if not items or not isinstance(items, list) or len(items) == 0:
            logger.error(f"Media with id '{media_id}' not found or has unexpected structure")
            raise HTTPException(
                status_code=HTTP_404_NOT_FOUND,
                detail=f"Media with id '{media_id}' not found or has unexpected structure",
                extra={"media_id": media_id})

        media = self._parse_media_json(json_data)
        return media
