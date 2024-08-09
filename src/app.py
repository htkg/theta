import os

from litestar import Litestar
from litestar.config.response_cache import ResponseCacheConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry
from structlog import get_logger

from src.helpers.log import log_conf
from src.helpers.middlewares import ProcessTimeHeader
from src.helpers.auth import login_handler, jwt_auth
from src.routes import route_handlers

logger = get_logger("Theta.app")
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'default_password')


def initialize_stores(app: Litestar):
    if not app.state.get("testing", False):
        redis = RedisStore.with_client(
            url=f"redis://redis:{REDIS_PORT}",
            password=REDIS_PASSWORD,
            namespace=None,
        )

        cache = redis.with_namespace("cache")
        users = redis.with_namespace("users")
        stores = StoreRegistry(stores={"cache": cache, "users": users})
        return stores


def startup(app: Litestar):
    logger.info("Starting up")
    app.stores = initialize_stores(app)
    logger.info(f"Theta API is running!")


def shutdown():
    logger.info("Shutting down")


app = Litestar(on_startup=[startup], on_shutdown=[shutdown], debug=True,
               middleware=[ProcessTimeHeader],
               on_app_init=[jwt_auth.on_app_init],
               route_handlers=route_handlers + [login_handler],
               plugins=[StructlogPlugin(log_conf)],
               response_cache_config=ResponseCacheConfig(default_expiration=None, store='cache'),
               openapi_config=OpenAPIConfig(
                   title="Theta",
                   description="Theta API",
                   version="0.0.1",
                   render_plugins=[ScalarRenderPlugin()],
               ),
               )
