import os

from litestar import Litestar
from litestar.config.response_cache import ResponseCacheConfig
from litestar.openapi import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry
from structlog import get_logger

from log import log_conf
from middleware.process_time import ProcessTimeHeader
from routes.routers import route_handlers

logger = get_logger("Theta.app")
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'default_password')
REDIS_NAMESPACE = os.getenv('REDIS_NAMESPACE', 'default_namespace')


def startup(app: Litestar):
    logger.info("Starting up")
    # Initialize RedisStore with environment variables
    redis = RedisStore.with_client(
        url=f"redis://redis:{REDIS_PORT}",
        password=REDIS_PASSWORD,
        namespace=REDIS_NAMESPACE
    )

    # Initialize StoreRegistry with the configured RedisStore
    stores = StoreRegistry(default_factory=redis.with_namespace)
    app.stores = stores
    logger.info(f"Theta API is running!")


def shutdown(app: Litestar):
    logger.info("Shutting down")
    # Close the Redis connection when the application shuts down
    app.stores = None


# Initialize the Litestar application with necessary configurations
app = Litestar(on_startup=[startup], on_shutdown=[shutdown],
               middleware=[ProcessTimeHeader],
               route_handlers=route_handlers,
               plugins=[StructlogPlugin(log_conf)],
               response_cache_config=ResponseCacheConfig(default_expiration=None),
               openapi_config=OpenAPIConfig(
                   title="Litestar Example",
                   description="Example of Litestar with Scalar OpenAPI docs",
                   version="0.0.1",
                   render_plugins=[ScalarRenderPlugin()],
               ),
               )
