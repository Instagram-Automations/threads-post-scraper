import time
import functools
from typing import Tuple, Optional


def retry(
    on_exceptions: Tuple[Exception, ...],
    tries: Optional[int] = None,
    max_tries_key: Optional[Tuple[str, str]] = None,
    backoff_seconds_key: Optional[Tuple[str, str]] = None,
):
    """
    Decorator for retrying a function with exponential backoff based on config present in `self.cfg`.
    If `tries` is None, reads from `self.cfg[max_tries_key]`. Same for backoff.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            cfg = getattr(self, "cfg", {}) or {}
            max_tries = tries
            if max_tries is None and max_tries_key:
                section, key = max_tries_key
                max_tries = int(cfg.get(section, {}).get(key, 3))
            max_tries = max(1, int(max_tries or 1))

            backoff = 1.0
            if backoff_seconds_key:
                section, key = backoff_seconds_key
                backoff = float(cfg.get(section, {}).get(key, 1.0))

            attempt = 0
            while True:
                try:
                    return func(self, *args, **kwargs)
                except on_exceptions as e:
                    attempt += 1
                    if attempt >= max_tries:
                        raise
                    time.sleep(backoff * attempt)
        return wrapper
    return decorator


def catch_exceptions(exit_code: int = 1):
    def decorator(main_func):
        @functools.wraps(main_func)
        def wrapper(*args, **kwargs):
            try:
                return main_func(*args, **kwargs)
            except SystemExit:
                raise
            except Exception as e:
                # Lazy import to avoid circular
                from .logger import get_logger
                log = get_logger("main")
                log.error(f"Fatal error: {e}", exc_info=True)
                return exit_code
        return wrapper
    return decorator
