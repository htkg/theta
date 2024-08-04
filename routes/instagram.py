from litestar import get, Controller

from modules.instagram import InstagramMediaFetcher, Media


class InstagramController(Controller):
    """Downloads images and videos from Instagram"""

    tags = ["Media"]
    path = "/instagram"

    @get("{instagram_id:str}")
    async def instagram_handler(self, instagram_id: str) -> Media | None:
        fetcher = InstagramMediaFetcher()
        media = await fetcher.get_instagram_media(instagram_id)

        return media
