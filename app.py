from litestar import Litestar, Request
from litestar import get
from litestar.plugins.structlog import StructlogPlugin

from log import logging_config
from middleware.process_time import ProcessTimeHeader
from routes.routers import route_handlers


@get("/")
async def root_handler(request: Request) -> None:
    request.logger.info("inside a request")
    return {"hello": "world"}


app = Litestar(middleware=[ProcessTimeHeader], route_handlers=route_handlers,
               plugins=[StructlogPlugin(logging_config)], debug=True)
