import logging

import uvicorn

from lingominer.logger import LOGGING_CONFIG, logger

if __name__ == "__main__":
    logger.info("Starting server")
    uvicorn.run(
        "lingominer.app:app",
        host="0.0.0.0",
        reload=True,
        log_config=LOGGING_CONFIG,
    )
