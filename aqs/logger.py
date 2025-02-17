import logging
import sys
from aqs.info import VERSION

# ANSI escape codes for colors
RESET = "\x1b[0m"
LEVEL_COLORS = {
    "DEBUG": "\x1b[34m",    # Blue
    "INFO": "\x1b[32m",     # Green
    "WARNING": "\x1b[33m",  # Yellow
    "ERROR": "\x1b[31m",    # Red
    "CRITICAL": "\x1b[41m", # Red background
}

LOGGER = logging.getLogger(f"AQS {VERSION}")

# Custom Formatter to meet our requirements.
class CustomFormatter(logging.Formatter):
    """
    Format:
    [colored level (3-letter)] [timestamp] [message (padded to 50 chars)] [filename:line]
    """
    def format(self, record):
        # Map the full level name to a 3-letter abbreviation.
        abbreviations = {
            "DEBUG": "DEB",
            "INFO": "INF",
            "WARNING": "WAR",
            "ERROR": "ERR",
            "CRITICAL": "CRI",
        }
        levelname = record.levelname.upper()
        short_level = abbreviations.get(levelname, levelname[:3])
        # Apply color to the level abbreviation.
        color = LEVEL_COLORS.get(levelname, "")
        colored_level = f"{color}{short_level}{RESET}"

        # Format the timestamp. We'll use a constant format so it's always 19 characters.
        record.asctime = self.formatTime(record, self.datefmt or "%Y-%m-%d %H:%M:%S")

        # Build a filename:line string.
        filename_line = f"{record.filename}:{record.lineno}"

        # Build the final log string. The message is padded to 50 characters.
        log_fmt = f"[{colored_level}] [%(asctime)-19s] [%(message)-50s] [{filename_line}]"
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)

def setup_logger(level, logfile=None):
    """
    Sets up the logger with the specified level.
    If logfile is provided, logging is also written to that file (without color codes).
    """
    global LOGGER
    
    # Convert loglevel argument (string) to a logging constant.
    level = getattr(logging, level.upper(), logging.DEBUG)
    LOGGER.setLevel(level)
    
    # Remove any pre-existing handlers.
    for handler in LOGGER.handlers[:]:
        LOGGER.removeHandler(handler)

    # Console handler with our custom formatter.
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(CustomFormatter())
    LOGGER.addHandler(console_handler)

    if logfile:
        # File handler: we use a plain formatter (no ANSI escape codes).
        file_fmt = "[%(levelname).3s] [%(asctime)-19s] [%(message)-50s] [%(filename)s:%(lineno)d]"
        file_formatter = logging.Formatter(file_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(file_formatter)
        LOGGER.addHandler(file_handler)
        