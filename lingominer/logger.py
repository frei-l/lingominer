import logging
import logging.config

# ANSI color codes
CYAN = "\033[36m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RED = "\033[31m"
RESET = "\033[0m"


class ColorFormatter(logging.Formatter):
    COLORS = {
        "DEBUG": CYAN,
        "INFO": GREEN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": RED,
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{RESET}"
            record.asctime = f"{CYAN}{self.formatTime(record, self.datefmt)}{RESET}"
        return super().format(record)


LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "colored": {
            "()": ColorFormatter,
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "colored",
            "stream": "ext://sys.stdout",
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console"],
            "propagate": False,
        },
        "uvicorn.error": {"level": "INFO"},
        "sqlalchemy": {"level": "WARNING"},
    },
}

logger = logging.getLogger("lingominer")
