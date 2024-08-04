from litestar import Litestar, Request
from litestar import get
from litestar.plugins.structlog import StructlogPlugin

from log import logging_config
from middleware.process_time import ProcessTimeHeader
from routes.instagram import instagram_router
from routes.nhentai import nhentai_router

@get("/")
async def root_handler(request: Request) -> None:
    request.logger.info("inside a request")
    return {"hello": "world"}


app = Litestar(middleware=[ProcessTimeHeader], route_handlers=[root_handler, instagram_router, nhentai_router],
               plugins=[StructlogPlugin(logging_config)], debug=True)
