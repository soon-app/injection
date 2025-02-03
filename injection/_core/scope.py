from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from collections.abc import Iterator, MutableMapping
from contextlib import AsyncExitStack, ExitStack, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
from functools import partial
from types import TracebackType
from typing import (
    Any,
    AsyncContextManager,
    ContextManager,
    Final,
    Protocol,
    Self,
    overload,
    runtime_checkable,
)

from injection._core.common.sentinel import sentinel

__scopes: Final[defaultdict[str, ContextVar[Scope]]] = defaultdict(
    partial(ContextVar, "python-injection-scope")
)


@overload
def get_scope[Default](scope_name: str, /, default: Default) -> Scope | Default: ...


@overload
def get_scope(scope_name: str, /, default: object = ...) -> Scope: ...


def get_scope(scope_name, /, default=sentinel):  # type: ignore[no-untyped-def]
    var = __scopes[scope_name]
    args = () if default is sentinel else (default,)

    try:
        return var.get(*args)
    except LookupError:
        # TODO: Scope not set
        raise


@contextmanager
def bind_scope(scope_name: str, /, value: Scope) -> Iterator[None]:
    var = __scopes[scope_name]

    if var.get(None):
        # TODO: Scope already set
        raise

    token = var.set(value)
    try:
        yield
    finally:
        var.reset(token)


@runtime_checkable
class Scope(Protocol):
    __slots__ = ()

    name: str
    cache: MutableMapping[Any, Any]

    @abstractmethod
    async def aenter[T](self, context_manager: AsyncContextManager[T]) -> T:
        raise NotImplementedError

    @abstractmethod
    def enter[T](self, context_manager: ContextManager[T]) -> T:
        raise NotImplementedError


@dataclass(repr=False, frozen=True, slots=True)
class AsyncScope(Scope):
    name: str
    cache: MutableMapping[Any, Any] = field(default_factory=dict, init=False)
    __exit_stack: AsyncExitStack = field(default_factory=AsyncExitStack, init=False)

    async def __aenter__(self) -> Self:
        await self.__exit_stack.__aenter__()
        lifetime = bind_scope(self.name, self)
        self.enter(lifetime)
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return await self.__exit_stack.__aexit__(exc_type, exc_value, traceback)

    async def aenter[T](self, context_manager: AsyncContextManager[T]) -> T:
        return await self.__exit_stack.enter_async_context(context_manager)

    def enter[T](self, context_manager: ContextManager[T]) -> T:
        return self.__exit_stack.enter_context(context_manager)


@dataclass(repr=False, frozen=True, slots=True)
class SyncScope(Scope):
    name: str
    cache: MutableMapping[Any, Any] = field(default_factory=dict, init=False)
    __exit_stack: ExitStack = field(default_factory=ExitStack, init=False)

    def __enter__(self) -> Self:
        self.__exit_stack.__enter__()
        lifetime = bind_scope(self.name, self)
        self.enter(lifetime)
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Any:
        return self.__exit_stack.__exit__(exc_type, exc_value, traceback)

    async def aenter[T](self, context_manager: AsyncContextManager[T]) -> T:
        # TODO: Unsupported operation
        raise

    def enter[T](self, context_manager: ContextManager[T]) -> T:
        return self.__exit_stack.enter_context(context_manager)
