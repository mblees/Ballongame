import logging

# ANSI color codes
COLORS = {
    "DEBUG": "\033[37m",   # White
    "INFO": "\033[36m",    # Cyan
    "WARNING": "\033[33m", # Yellow
    "ERROR": "\033[31m",   # Red
    "CRITICAL": "\033[41m" # Red background
}
RESET = "\033[0m"

class ColorFormatter(logging.Formatter):
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname:<8}{RESET}"
        return super().format(record)

formatter = ColorFormatter(
    fmt="%(asctime)s | %(levelname)s | %(name)-15s | %(message)s",
    datefmt="%H:%M:%S"
)

def activate_logging_config(level=logging.DEBUG):
    handler = logging.StreamHandler()
    handler.setFormatter(formatter)

    logger = logging.getLogger()
    logger.setLevel(level)
    logger.handlers.clear()  # avoid duplicate logs
    logger.addHandler(handler)
    return logger
