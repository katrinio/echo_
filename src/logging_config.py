import logging


_LOG_FORMAT = "%(asctime)s %(levelname)-5s %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def configure_logging() -> None:
    root_logger = logging.getLogger()

    if root_logger.handlers:
        root_logger.handlers[0].setFormatter(logging.Formatter(_LOG_FORMAT, _DATE_FORMAT))
        root_logger.setLevel(logging.INFO)
        return

    logging.basicConfig(
        level=logging.INFO,
        format=_LOG_FORMAT,
        datefmt=_DATE_FORMAT,
    )
