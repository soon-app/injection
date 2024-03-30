from contextlib import ContextDecorator, contextmanager
from threading import RLock
from typing import ContextManager

__all__ = ("synchronized",)

__thread_lock = RLock()


@contextmanager
def synchronized() -> ContextManager | ContextDecorator:
    with __thread_lock:
        yield
