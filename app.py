import structlog
from litestar import Litestar, Request, get
from litestar.logging import StructLoggingConfig
from litestar.logging.config import default_structlog_processors, default_json_serializer
from litestar.plugins.structlog import StructlogConfig, StructlogPlugin
from pathlib import Path
log_file = Path(__file__).parent / 'log.log'

logging_config = StructlogConfig(
    structlog_logging_config=StructLoggingConfig(
        logger_factory=structlog.WriteLoggerFactory(file=log_file.open("wt")),
        processors=default_structlog_processors(
            json_serializer=lambda v, **_: str(default_json_serializer(v), "utf-8")
        ),
    ),
)
logger = structlog.get_logger()

@get("/")
async def handler(request: Request) -> None:
    request.logger.info("inside a request")
    return None

app = Litestar(route_handlers=[handler], plugins=[StructlogPlugin(config=logging_config)], debug=True)