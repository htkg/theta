from litestar.types import ControllerRouterHandler

from src.routes.instagram import InstagramController
from src.routes.main import MainController
from src.routes.nhentai import NHentaiController

route_handlers: list[ControllerRouterHandler] = [
    InstagramController,
    NHentaiController,
    MainController
]
