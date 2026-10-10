# ============================================
# NEXORA AI - Logging Configuration
# ============================================
# Loguru ব্যবহার করে professional logging setup।
# Console + File উভয়তেই log লেখা হয়।

import sys
from loguru import logger
from app.core.config import settings

# Default logger সরিয়ে custom configuration দেওয়া
logger.remove()

# Console output - colorful & readable
logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.DEBUG else "INFO",
)

# File output - সব logs সংরক্ষণ
logger.add(
    "logs/nexora_{time:YYYY-MM-DD}.log",
    rotation="1 day",      # প্রতিদিন নতুন log file
    retention="7 days",    # ৭ দিন পুরনো logs রাখা হয়
    compression="zip",     # পুরনো logs compress করা
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function} - {message}",
)

# Export করা হচ্ছে যাতে সব জায়গায় import করা যায়
__all__ = ["logger"]
