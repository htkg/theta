import random

from httpx._exceptions import HTTPStatusError
from litestar import get, Controller
from litestar.exceptions import NotFoundException, HTTPException

from src.modules.nhentai import NhentaiAPI, NhentaiGallery


class NHentaiController(Controller):
    """Downloads images and videos from Instagram"""

    tags = ["Media"]
    path = "/nhentai"


    @get("{nh_id:int}", cache=True, description="Gets doujinshi / manga from NHentai", summary="Get doujinshi")
    async def nhentai_handler(self, nh_id: int) -> NhentaiGallery:
        fetcher = NhentaiAPI()

        try:
            media = await fetcher.get_gallery(nh_id)
        except HTTPStatusError as e:
            if e.response.status_code == 404:
                raise NotFoundException(detail="Not found")
            else:
                raise HTTPException(detail=str(e))

        return media

    @get("/random", description="Gets random doujinshi / manga from NHentai", summary="Get random doujinshi")
    async def random_handler(self) -> NhentaiGallery:
        fetcher = NhentaiAPI()
        upper_limit = 522723
        lower_limit = 1
        random_number = random.randint(lower_limit, upper_limit)
        try:
            media = await fetcher.get_gallery(random_number)
        except HTTPStatusError:
            random_number = random.randint(lower_limit, upper_limit)
            media = await fetcher.get_gallery(random_number)

        return media
