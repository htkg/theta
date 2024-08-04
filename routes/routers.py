from litestar.types import ControllerRouterHandler

from routes.instagram import InstagramController
from routes.main import MainController
from routes.nhentai import NHentaiController

route_handlers: list[ControllerRouterHandler] = [
    InstagramController,
    NHentaiController,
    MainController
]
