from litestar import get, Controller

from modules.nhentai import NhentaiAPI, NhentaiGallery


class NHentaiController(Controller):
    """Downloads images and videos from Instagram"""

    tags = ["NSFW", "Media"]
    path = "/nhentai"

    @get("{nh_id:int}")
    async def nhentai_handler(self, nh_id: int) -> NhentaiGallery:
        fetcher = NhentaiAPI()
        media = await fetcher.get_gallery(nh_id)

        return media
