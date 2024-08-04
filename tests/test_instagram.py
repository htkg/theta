import pytest
from litestar.status_codes import HTTP_200_OK
from litestar.testing import AsyncTestClient

from src.app import app as _app, initialize_stores

reels = {
    "id": "C-QNymBI4BW",
    "tags": [
        "coding",
        "computerscience",
        "softwareengineer",
        "devlife",
        "cs",
        "learningtocode",
        "learntocode",
        "100daysofcode"
    ],
}


@pytest.fixture
def app():
    _app.state.testing = True
    initialize_stores(_app)
    return _app


@pytest.mark.asyncio
async def test_instagram_reel(app):
    async with AsyncTestClient(app=app) as client:
        response = await client.get("/instagram/C-QNymBI4BW")
        json_response = response.json()
        assert response.status_code == HTTP_200_OK
        assert json_response['tags'] == reels['tags']
