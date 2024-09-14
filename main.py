from langfuse import Langfuse
from dotenv import load_dotenv
import uvicorn
from lingominer.logger import logger, LOGGING_CONFIG
import logging

load_dotenv()
langfuse = Langfuse()
# check authorization
assert langfuse.auth_check()

if __name__ == "__main__":
    logger.info("Starting server")
    uvicorn.run(
        "lingominer.api:app",
        host="127.0.0.1",
        port=7875,
        reload=True,
        log_config=LOGGING_CONFIG,
        log_level=logging.INFO,
    )
