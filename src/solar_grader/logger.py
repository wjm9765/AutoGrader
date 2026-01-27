from loguru import logger
import sys
import os

# Create logs directory if it doesn't exist
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# Remove default handler
logger.remove()

# Add console handler
logger.add(sys.stderr, format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>")

# Add file handler
logger.add(os.path.join(log_dir, "solar_grader.log"), rotation="10 MB", retention="10 days", level="DEBUG")

def get_logger():
    return logger
