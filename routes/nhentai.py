from litestar import get, Controller
import random

from modules.nhentai import NhentaiAPI, NhentaiGallery


class NHentaiController(Controller):
    """Downloads images and videos from Instagram"""

    tags = ["Media"]
    path = "/nhentai"

    @get("{nh_id:int}")
    async def nhentai_handler(self, nh_id: int) -> NhentaiGallery:
        fetcher = NhentaiAPI()
        media = await fetcher.get_gallery(nh_id)

        return media

    @get("/random")
    async def random_handler(self) -> NhentaiGallery:
        fetcher = NhentaiAPI()
        upper_limit = 522723
        lower_limit = 1
        random_number = random.randint(lower_limit, upper_limit)
        media = await fetcher.get_gallery(random_number)
        return media
