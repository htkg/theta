from litestar import Litestar, Request
from litestar import get
from litestar.plugins.structlog import StructlogPlugin

from log import logging_config
from middleware.process_time import ProcessTimeHeader


@get("/")
async def my_router_handler(request: Request) -> None:
    request.logger.info("inside a request")
    return {"hello": "world"}


@get("/books/{book_id:int}")
async def get_book(book_id: int) -> dict[str, int]:
    return {"book_id": book_id}


app = Litestar(middleware=[ProcessTimeHeader], route_handlers=[my_router_handler, get_book],
               plugins=[StructlogPlugin(logging_config)])
