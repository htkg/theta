import pytest
from litestar.status_codes import HTTP_200_OK, HTTP_404_NOT_FOUND
from litestar.testing import AsyncTestClient

from src.app import app as _app, initialize_stores


@pytest.fixture
def app():
    _app.state.testing = True
    initialize_stores(_app)
    return _app


@pytest.mark.asyncio
async def test_nhentai_by_id(app):
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/nhentai/489600")
        assert response.status_code in [HTTP_200_OK, HTTP_404_NOT_FOUND]

        if response.status_code == HTTP_200_OK:
            json_response = response.json()
            assert json_response['id'] == 489600
            assert json_response['title']['pretty'] == "Kiyoki Kororo to Amai Ame"
        else:
            assert response.json()['detail'] == "Gallery not found"


@pytest.mark.asyncio
async def test_nhentai_random(app):
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/nhentai/random")
        assert response.status_code in [HTTP_200_OK, HTTP_404_NOT_FOUND]

        if response.status_code == HTTP_200_OK:
            json_response = response.json()
            assert json_response['id'] is not None
            assert json_response['title'] is not None
        else:
            assert response.json()['detail'] == "Gallery not found"
