import logging
import sys
from functools import lru_cache

from litestar.logging import StructLoggingConfig
from litestar.logging.config import (
    default_structlog_processors,
    LoggingConfig, )
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig


@lru_cache
def _is_tty() -> bool:
    return bool(sys.stderr.isatty() or sys.stdout.isatty())


_render_as_json = not _is_tty()
_structlog_processors = default_structlog_processors(as_json=_render_as_json)

log_conf = StructlogConfig(enable_middleware_logging=True,
                           structlog_logging_config=StructLoggingConfig(
                               log_exceptions="always",
                               standard_lib_logging_config=LoggingConfig(
                                   root={"level": logging.getLevelName(20), "handlers": ["queue_listener"]},
                                   loggers={
                                       "uvicorn.access": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                       "uvicorn.error": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                       "granian.access": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                       "granian.error": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                       "watchfiles": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                       "httpx": {
                                           "propagate": False,
                                           "level": 100,
                                           "handlers": ["queue_listener"],
                                       },
                                   },
                               ),
                           ),
                           middleware_logging_config=LoggingMiddlewareConfig(
                               request_log_fields=["method", "path", "path_params", "query", "headers"],
                               response_log_fields=["status_code", "headers"],
                           ),
                           )
