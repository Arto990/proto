import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from .constants import LOGS_DIR

def get_logger(name: str) -> logging.Logger:
    """
    Returns a logger that writes to BOTH console and a rotating file.
    No print() anywhere in the codebase.
    """
    logger = logging.getLogger(name)
    if logger.handlers:  # already configured
        return logger

    logger.setLevel(logging.INFO)

    # File handler
    log_file: Path = LOGS_DIR / "protocheck.log"
    file_h = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3)
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_h.setFormatter(fmt)

    # Console handler
    console_h = logging.StreamHandler()
    console_h.setFormatter(fmt)

    logger.addHandler(file_h)
    logger.addHandler(console_h)
    logger.propagate = False  # avoid duplicate messages

    logger.info("Logger initialized (file: %s)", log_file)
    return logger
