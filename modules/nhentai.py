import httpx
from typing import Dict, List
from dataclasses import dataclass, fields


@dataclass(frozen=True)
class Title:
    english: str
    japanese: str
    pretty: str

@dataclass(frozen=True)
class Tag:
    id: int
    type: str
    name: str
    url: str
    count: int

@dataclass(frozen=True)
class Images:
    pages: List[str]
    cover: str
    thumbnail: str

@dataclass(frozen=True)
class NhentaiGallery:
    id: int
    media_id: int
    title: Title
    images: Images
    scanlator: str
    upload_date: int
    tags: List[Tag]
    num_pages: int
    num_favorites: int

class NhentaiAPI:
    base_url: str = "https://nhentai.net"

    @staticmethod
    async def fetch_gallery_data(gallery_id: int) -> dict:
        """ Fetch data from nhentai API for the provided gallery ID. """
        api_url = f"{NhentaiAPI.base_url}/api/gallery/{gallery_id}"
        async with httpx.AsyncClient() as client:
            response = await client.get(api_url)
            response.raise_for_status()
            return response.json()

    @staticmethod
    def parse_title(data: dict) -> Title:
        """ Parse the title information from the provided data. """
        return Title(**data['title'])

    @staticmethod
    def parse_tags(data: dict) -> List[Tag]:
        """ Parse the tags information from the provided data. """
        return [Tag(**tag) for tag in data['tags']]

    @staticmethod
    def parse_images(data: dict) -> Images:
        """ Parse the images information from the provided data. """
        pages_urls = []
        for i, page in enumerate(data['images']['pages'], start=1):
            ext = {
                'j': 'jpg',
                'p': 'png',
                'g': 'gif'
            }.get(page['t'], 'jpg')
            img_url = f"https://i.nhentai.net/galleries/{data['media_id']}/{i}.{ext}"
            pages_urls.append(img_url)
        cover_url = f"https://i.nhentai.net/galleries/{data['media_id']}/cover.jpg"
        thumbnail_url = f"https://t.nhentai.net/galleries/{data['media_id']}/thumb.jpg"
        return Images(pages=pages_urls, cover=cover_url, thumbnail=thumbnail_url)

    @staticmethod
    async def get_gallery(gallery_id: int) -> NhentaiGallery:
        """ Get NhentaiGallery object containing all metadata and image URLs. """
        data = await NhentaiAPI.fetch_gallery_data(gallery_id)
        title = NhentaiAPI.parse_title(data)
        tags = NhentaiAPI.parse_tags(data)
        images = NhentaiAPI.parse_images(data)
        return NhentaiGallery(
            id=data['id'],
            media_id=int(data['media_id']),
            title=title,
            images=images,
            scanlator=data.get('scanlator', ''),
            upload_date=data['upload_date'],
            tags=tags,
            num_pages=data['num_pages'],
            num_favorites=data['num_favorites']
        )
