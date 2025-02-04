from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from collections.abc import Iterator, MutableMapping
from contextlib import AsyncExitStack, ExitStack, contextmanager
from contextvars import ContextVar
from dataclasses import dataclass, field
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
from weakref import WeakSet

from injection._core.common.key import new_short_key
from injection._core.common.sentinel import sentinel
from injection.exceptions import (
    ScopeAlreadyDefinedError,
    ScopeError,
    ScopeUndefinedError,
)


@dataclass(repr=False, frozen=True, slots=True)
class _GlobalScope:
    context_var: ContextVar[Scope] = field(
        default_factory=lambda: ContextVar(f"scope@{new_short_key()}"),
        init=False,
    )
    references: WeakSet[Scope] = field(
        default_factory=WeakSet,
        init=False,
    )

    def to_tuple(self) -> tuple[ContextVar[Scope], WeakSet[Scope]]:
        return self.context_var, self.references


__SCOPES: Final[defaultdict[str, _GlobalScope]] = defaultdict(_GlobalScope)


@contextmanager
def bind_scope(scope_name: str, /, value: Scope) -> Iterator[None]:
    var, references = __SCOPES[scope_name].to_tuple()

    if var.get(None):
        raise ScopeAlreadyDefinedError(
            f"Scope `{scope_name}` is already defined in the current context."
        )

    references.add(value)
    token = var.set(value)

    try:
        yield
    finally:
        var.reset(token)
        references.discard(value)
        value.cache.clear()


def get_active_scopes(scope_name: str, /) -> tuple[Scope, ...]:
    return tuple(__SCOPES[scope_name].references)


@overload
def get_scope[Default](scope_name: str, /, default: Default) -> Scope | Default: ...


@overload
def get_scope(scope_name: str, /, default: object = ...) -> Scope: ...


def get_scope(scope_name, /, default=sentinel):  # type: ignore[no-untyped-def]
    var = __SCOPES[scope_name].context_var
    args = () if default is sentinel else (default,)

    try:
        return var.get(*args)
    except LookupError as exc:
        raise ScopeUndefinedError(
            f"Scope `{scope_name}` isn't defined in the current context."
        ) from exc


@runtime_checkable
class Scope(Protocol):
    __slots__ = ("__weakref__",)

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
        raise ScopeError("SyncScope doesn't support asynchronous context manager.")

    def enter[T](self, context_manager: ContextManager[T]) -> T:
        return self.__exit_stack.enter_context(context_manager)
