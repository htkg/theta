from litestar import Router, get
from modules.instagram import InstagramMediaFetcher

@get("/{instagram_id:str}")
async def instagram_handler(instagram_id: str) -> None:
    fetcher = InstagramMediaFetcher()
    media = fetcher.get_instagram_media(instagram_id)
    
    return media


instagram_router = Router(path="/instagram", route_handlers=[instagram_handler])