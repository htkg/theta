import os
from litestar import Litestar, Request, get
from litestar.config.response_cache import ResponseCacheConfig
from litestar.plugins.structlog import StructlogPlugin
from litestar.stores.redis import RedisStore
from litestar.stores.registry import StoreRegistry
from log import logging_config
from middleware.process_time import ProcessTimeHeader
from routes.routers import route_handlers

# Load environment variables
REDIS_HOST = os.getenv('REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('REDIS_PORT', '6379')
REDIS_PASSWORD = os.getenv('REDIS_PASSWORD', 'default_password')
REDIS_NAMESPACE = os.getenv('REDIS_NAMESPACE', 'default_namespace')
# Initialize RedisStore with environment variables
redis = RedisStore.with_client(
    url=f"redis://redis:{REDIS_PORT}",
    password=REDIS_PASSWORD,
    namespace=REDIS_NAMESPACE
)

# Initialize StoreRegistry with the configured RedisStore
stores = StoreRegistry(default_factory=redis.with_namespace)

@get("/")
async def root_handler() -> dict:
    return {"hello": "world"}

# Initialize the Litestar application with necessary configurations
app = Litestar(
    middleware=[ProcessTimeHeader],
    route_handlers=route_handlers,
    plugins=[StructlogPlugin(logging_config)],
    debug=True,
    stores=stores,
    response_cache_config=ResponseCacheConfig(default_expiration=None)
)
