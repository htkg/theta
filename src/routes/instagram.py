from litestar import get, Controller

from src.modules.instagram import InstagramMediaFetcher, Media


class InstagramController(Controller):
    """Downloads images and videos from Instagram"""

    tags = ["Media"]
    path = "/instagram"

    @get("{instagram_id:str}", cache=86400, description="Get post or reel from Instagram",
         summary="Get post or reel from Instagram")
    async def instagram_handler(self, instagram_id: str) -> Media:
        fetcher = InstagramMediaFetcher()
        media = await fetcher.get_instagram_media(instagram_id)

        return media
