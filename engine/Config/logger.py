import logging
from logging.handlers import RotatingFileHandler
import os


LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


def configure_logger(logging_config: dict) -> logging.Logger:
    """Configure and return an application logger based on CONFIG.logging.

    If logging is disabled, a no-op logger is returned (logs are suppressed).
    """
    logger = logging.getLogger("NoveraAI")

    enabled = bool(logging_config.get("enabled", False))
    if not enabled:
        # Disable all logging output
        logging.disable(logging.CRITICAL)
        return logger

    level_name = str(logging_config.get("level", "INFO")).upper()
    level = LEVEL_MAP.get(level_name, logging.INFO)

    logger.setLevel(level)

    # Avoid duplicate handlers when reconfiguring
    if logger.handlers:
        return logger

    log_path = logging_config.get("log_path", "Data/AI_debug.log")
    log_dir = os.path.dirname(os.path.abspath(log_path))
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    file_handler = RotatingFileHandler(log_path, maxBytes=2_000_000, backupCount=5, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    return logger


