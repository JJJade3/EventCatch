import logging

_configured = False


def configure_logging(level: int = logging.INFO) -> None:
    global _configured
    if _configured:
        return
    logging.basicConfig(level=level, format="%(asctime)s | %(levelname)s | %(message)s")
    _configured = True
