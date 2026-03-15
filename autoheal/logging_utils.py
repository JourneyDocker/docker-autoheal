"""Logging utilities for Docker Autoheal."""

import logging
from datetime import datetime


class CustomFormatter(logging.Formatter):
    """Custom formatter for log messages."""

    def format(self, record):
        timestamp = datetime.now().strftime("%I:%M:%S %p")
        level = record.levelname
        message = record.getMessage()

        if level == "DEBUG":
            return f"[{timestamp}] 🔍 DEBUG: {message}"
        elif level == "INFO":
            return f"[{timestamp}] ℹ️ INFO: {message}"
        elif level == "WARNING":
            return f"[{timestamp}] ⚠️ WARN: {message}"
        elif level == "ERROR":
            return f"[{timestamp}] ❌ ERROR: {message}"
        return f"[{timestamp}] {level}: {message}"


_logger = None


def get_logger() -> logging.Logger:
    """Get the logger, setting it up if not already."""
    global _logger
    if _logger is None:
        _logger = logging.getLogger("autoheal")
        _logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        handler.setFormatter(CustomFormatter())
        _logger.addHandler(handler)
    return _logger


def setup_logging(log_level: int) -> logging.Logger:
    """Set up logging level."""
    logger = get_logger()
    logger.setLevel(logging.DEBUG if log_level == 2 else logging.INFO)
    return logger
