import anyio
from litestar import Controller, get, Response


class MainController(Controller):
    path = "/"

    opt = {"exclude_from_auth": True}
    include_in_schema = False

    @get(path="/favicon.ico")
    async def favicon(self) -> Response:
        # Ensure proper use of async context with AnyIO
        async with await anyio.open_file("static/favicon.ico", "rb") as file:
            ico = await file.read()

        # Return the icon with the correct media type
        return Response(content=ico, media_type="image/x-icon")
