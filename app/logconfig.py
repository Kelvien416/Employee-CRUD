# import logging
from pathlib import Path
import structlog

def log_config():        
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(), 
        ],
        logger_factory=structlog.WriteLoggerFactory(
            file=Path("file.log").open("wt")
        ),
    )

    log = structlog.get_logger()

    return log