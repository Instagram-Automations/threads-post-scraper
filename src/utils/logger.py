import logging
import json as _json
from logging import Logger
from typing import Optional


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return _json.dumps(payload, ensure_ascii=False)


def get_logger(name: str = "app", level: str = "INFO", json_mode: bool = False, log_file: Optional[str] = None) -> Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    if json_mode:
        formatter = _JsonFormatter()
    else:
        formatter = logging.Formatter("[%(levelname)s] %(name)s - %(message)s")

    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    if log_file:
        fh = logging.FileHandler(log_file, encoding="utf-8")
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger
