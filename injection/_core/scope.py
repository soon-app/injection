from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from collections.abc import Iterator, MutableMapping
from contextlib import (
    AsyncContextDecorator,
    AsyncExitStack,
    ContextDecorator,
    ExitStack,
    contextmanager,
)
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
    runtime_checkable,
)

from injection._core.common.key import new_short_key
from injection.exceptions import (
    ScopeAlreadyDefinedError,
    ScopeError,
    ScopeUndefinedError,
)


@dataclass(repr=False, frozen=True, slots=True)
class _ActiveScope:
    # Shouldn't be instantiated outside `__SCOPES`.

    context_var: ContextVar[Scope] = field(
        default_factory=lambda: ContextVar(f"scope@{new_short_key()}"),
        init=False,
    )
    references: set[Scope] = field(
        default_factory=set,
        init=False,
    )

    def to_tuple(self) -> tuple[ContextVar[Scope], set[Scope]]:
        return self.context_var, self.references


__SCOPES: Final[defaultdict[str, _ActiveScope]] = defaultdict(_ActiveScope)


@contextmanager
def bind_scope(name: str, value: Scope) -> Iterator[None]:
    context_var, references = __SCOPES[name].to_tuple()

    if context_var.get(None):
        raise ScopeAlreadyDefinedError(
            f"Scope `{name}` is already defined in the current context."
        )

    references.add(value)
    token = context_var.set(value)

    try:
        yield
    finally:
        context_var.reset(token)
        references.discard(value)
        value.cache.clear()


def get_active_scopes(name: str) -> tuple[Scope, ...]:
    return tuple(__SCOPES[name].references)


def get_scope(name: str) -> Scope:
    context_var = __SCOPES[name].context_var

    try:
        return context_var.get()
    except LookupError as exc:
        raise ScopeUndefinedError(
            f"Scope `{name}` isn't defined in the current context."
        ) from exc


@runtime_checkable
class Scope(Protocol):
    __slots__ = ()

    cache: MutableMapping[Any, Any]

    @abstractmethod
    async def aenter[T](self, context_manager: AsyncContextManager[T]) -> T:
        raise NotImplementedError

    @abstractmethod
    def enter[T](self, context_manager: ContextManager[T]) -> T:
        raise NotImplementedError


@dataclass(repr=False, frozen=True, slots=True)
class AsyncScope(AsyncContextDecorator, Scope):
    name: str
    cache: MutableMapping[Any, Any] = field(
        default_factory=dict,
        init=False,
        hash=False,
    )
    __exit_stack: AsyncExitStack = field(
        default_factory=AsyncExitStack,
        init=False,
    )

    async def __aenter__(self) -> Self:
        await self.__exit_stack.__aenter__()
        lifespan = bind_scope(self.name, self)
        self.enter(lifespan)
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
class SyncScope(ContextDecorator, Scope):
    name: str
    cache: MutableMapping[Any, Any] = field(
        default_factory=dict,
        init=False,
        hash=False,
    )
    __exit_stack: ExitStack = field(
        default_factory=ExitStack,
        init=False,
    )

    def __enter__(self) -> Self:
        self.__exit_stack.__enter__()
        lifespan = bind_scope(self.name, self)
        self.enter(lifespan)
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
