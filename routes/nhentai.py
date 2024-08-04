from litestar import Router, get
from modules.nhentai import NhentaiAPI, NhentaiGallery


@get("/{nh_id:int}")
async def nhentai_handler(nh_id: int) -> NhentaiGallery:
    fetcher = NhentaiAPI()
    media = fetcher.get_gallery(nh_id)

    return media


nhentai_router = Router(path="/nhentai", route_handlers=[nhentai_handler])

