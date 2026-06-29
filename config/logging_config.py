from pathlib import Path
import logging


def setup_logger(log_name: str) -> logging.Logger:
    """
    Create a logger that writes to both:
        - Terminal
        - logs/<log_name>.log
    """

    project_root = Path(__file__).resolve().parent.parent

    log_folder = project_root / "logs"
    log_folder.mkdir(exist_ok=True)

    logger = logging.getLogger(log_name)

    # Prevent duplicate handlers if imported multiple times
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # -----------------------------
    # File handler
    # -----------------------------
    file_handler = logging.FileHandler(
        log_folder / f"{log_name}.log", mode= 'w',
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # -----------------------------
    # Console handler
    # -----------------------------
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger