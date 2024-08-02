import logging
from pathlib import Path

import structlog
from litestar.logging import StructLoggingConfig
from litestar.logging.config import (
    default_structlog_processors,
    default_json_serializer,
    default_structlog_standard_lib_processors,
    LoggingConfig,
)
from litestar.middleware.logging import LoggingMiddlewareConfig
from litestar.plugins.structlog import StructlogConfig
from structlog import WriteLoggerFactory

log_file = Path(__file__).parent / 'log.log'
_structlog_processors = default_structlog_processors()
logging_config = StructlogConfig(enable_middleware_logging=True,
                                 structlog_logging_config=StructLoggingConfig(pretty_print_tty=True,
                                                                              log_exceptions="always",
                                                                              standard_lib_logging_config=LoggingConfig(
                                                                                  root={
                                                                                      "level": logging.getLevelName(20),
                                                                                      "handlers": ["queue_listener"]},
                                                                                  formatters={
                                                                                      "standard": {
                                                                                          "()": structlog.stdlib.ProcessorFormatter,
                                                                                          "processors": default_structlog_standard_lib_processors(
                                                                                              as_json=True),
                                                                                      }
                                                                                  }
                                                                              ),
                                                                              logger_factory=WriteLoggerFactory(
                                                                                  file=log_file.open("wt")),
                                                                              processors=default_structlog_processors(
                                                                                  json_serializer=lambda v, **_: str(
                                                                                      default_json_serializer(v),
                                                                                      "utf-8")
                                                                              ),
                                                                              ),
                                 middleware_logging_config=LoggingMiddlewareConfig(
                                     request_log_fields=["method", "path", "path_params", "query"],
                                     response_log_fields=["status_code"],
                                 ),
                                 )
