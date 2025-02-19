from abc import abstractmethod
from collections.abc import AsyncIterator, Awaitable, Callable, Iterator
from contextlib import asynccontextmanager, contextmanager
from enum import Enum
from logging import Logger
from typing import Any, Final, Protocol, Self, final, overload, runtime_checkable

from ._core.common.invertible import Invertible as _Invertible
from ._core.common.type import InputType as _InputType
from ._core.common.type import TypeInfo as _TypeInfo
from ._core.module import InjectableFactory as _InjectableFactory
from ._core.module import ModeStr, PriorityStr

__MODULE: Final[Module] = ...

afind_instance = __MODULE.afind_instance
aget_instance = __MODULE.aget_instance
aget_lazy_instance = __MODULE.aget_lazy_instance
constant = __MODULE.constant
find_instance = __MODULE.find_instance
get_instance = __MODULE.get_instance
get_lazy_instance = __MODULE.get_lazy_instance
inject = __MODULE.inject
injectable = __MODULE.injectable
scoped = __MODULE.scoped
set_constant = __MODULE.set_constant
should_be_injectable = __MODULE.should_be_injectable
singleton = __MODULE.singleton

@asynccontextmanager
def adefine_scope(name: str, *, shared: bool = ...) -> AsyncIterator[None]: ...
@contextmanager
def define_scope(name: str, *, shared: bool = ...) -> Iterator[None]: ...
def mod(name: str = ..., /) -> Module:
    """
    Short syntax for `Module.from_name`.
    """
@runtime_checkable
class Injectable[T](Protocol):
    @property
    def is_locked(self) -> bool: ...
    def unlock(self) -> None: ...
    @abstractmethod
    async def aget_instance(self) -> T: ...
    @abstractmethod
    def get_instance(self) -> T: ...

class LazyInstance[T]:
    def __init__(
        self,
        cls: _InputType[T],
        /,
        default: T = ...,
        module: Module = ...,
    ) -> None: ...
    @overload
    def __get__(self, instance: object, owner: type | None = ...) -> T: ...
    @overload
    def __get__(self, instance: None = ..., owner: type | None = ...) -> Self: ...

@final
class Module:
    """
    Object with isolated injection environment.

    Modules have been designed to simplify unit test writing. So think carefully before
    instantiating a new one. They could increase complexity unnecessarily if used
    extensively.
    """

    name: str

    def __init__(self, name: str = ...) -> None: ...
    def __contains__(self, cls: _InputType[Any], /) -> bool: ...
    @property
    def is_locked(self) -> bool: ...
    def inject[**P, T](self, wrapped: Callable[P, T] = ..., /) -> Any:
        """
        Decorator applicable to a class or function. Inject function dependencies using
        parameter type annotations. If applied to a class, the dependencies resolved
        will be those of the `__init__` method.
        """

    def injectable[**P, T](
        self,
        wrapped: Callable[P, T] | Callable[P, Awaitable[T]] = ...,
        /,
        *,
        cls: _InjectableFactory[T] = ...,
        inject: bool = ...,
        on: _TypeInfo[T] = ...,
        mode: Mode | ModeStr = ...,
    ) -> Any:
        """
        Decorator applicable to a class or function. It is used to indicate how the
        injectable will be constructed. At injection time, a new instance will be
        injected each time.
        """

    def singleton[**P, T](
        self,
        wrapped: Callable[P, T] | Callable[P, Awaitable[T]] = ...,
        /,
        *,
        inject: bool = ...,
        on: _TypeInfo[T] = ...,
        mode: Mode | ModeStr = ...,
    ) -> Any:
        """
        Decorator applicable to a class or function. It is used to indicate how the
        singleton will be constructed. At injection time, the injected instance will
        always be the same.
        """

    def scoped[**P, T](
        self,
        scope_name: str,
        /,
        *,
        inject: bool = ...,
        on: _TypeInfo[T] = (),
        mode: Mode | ModeStr = ...,
    ) -> Any:
        """
        Decorator applicable to a class or function or generator function. It is used
        to indicate how the scoped instance will be constructed. At injection time, the
        injected instance is retrieved from the scope.
        """

    def should_be_injectable[T](self, wrapped: type[T] = ..., /) -> Any:
        """
        Decorator applicable to a class. It is used to specify whether an injectable
        should be registered. Raise an exception at injection time if the class isn't
        registered.
        """

    def constant[T](
        self,
        wrapped: type[T] = ...,
        /,
        *,
        on: _TypeInfo[T] = ...,
        mode: Mode | ModeStr = ...,
    ) -> Any:
        """
        Decorator applicable to a class or function. It is used to indicate how the
        constant is constructed. At injection time, the injected instance will always
        be the same. Unlike `@singleton`, dependencies will not be resolved.
        """

    def set_constant[T](
        self,
        instance: T,
        on: _TypeInfo[T] = ...,
        *,
        alias: bool = ...,
        mode: Mode | ModeStr = ...,
    ) -> Self:
        """
        Function for registering a specific instance to be injected. This is useful for
        registering global variables. The difference with the singleton decorator is
        that no dependencies are resolved, so the module doesn't need to be locked.
        """

    def make_injected_function[**P, T](
        self,
        wrapped: Callable[P, T],
        /,
    ) -> Callable[P, T]: ...
    async def afind_instance[T](self, cls: _InputType[T]) -> T: ...
    def find_instance[T](self, cls: _InputType[T]) -> T:
        """
        Function used to retrieve an instance associated with the type passed in
        parameter or an exception will be raised.
        """

    @overload
    async def aget_instance[T, Default](
        self,
        cls: _InputType[T],
        default: Default,
    ) -> T | Default: ...
    @overload
    async def aget_instance[T](
        self,
        cls: _InputType[T],
        default: None = ...,
    ) -> T | None: ...
    @overload
    def get_instance[T, Default](
        self,
        cls: _InputType[T],
        default: Default,
    ) -> T | Default:
        """
        Function used to retrieve an instance associated with the type passed in
        parameter or return `None`.
        """

    @overload
    def get_instance[T](
        self,
        cls: _InputType[T],
        default: None = ...,
    ) -> T | None: ...
    @overload
    def aget_lazy_instance[T, Default](
        self,
        cls: _InputType[T],
        default: Default,
        *,
        cache: bool = ...,
    ) -> Awaitable[T | Default]: ...
    @overload
    def aget_lazy_instance[T](
        self,
        cls: _InputType[T],
        default: None = ...,
        *,
        cache: bool = ...,
    ) -> Awaitable[T | None]: ...
    @overload
    def get_lazy_instance[T, Default](
        self,
        cls: _InputType[T],
        default: Default,
        *,
        cache: bool = ...,
    ) -> _Invertible[T | Default]:
        """
        Function used to retrieve an instance associated with the type passed in
        parameter or `None`. Return a `Invertible` object. To access the instance
        contained in an invertible object, simply use a wavy line (~).
        With `cache=True`, the instance retrieved will always be the same.

        Example: instance = ~lazy_instance
        """

    @overload
    def get_lazy_instance[T](
        self,
        cls: _InputType[T],
        default: None = ...,
        *,
        cache: bool = ...,
    ) -> _Invertible[T | None]: ...
    def init_modules(self, *modules: Module) -> Self:
        """
        Function to clean modules in use and to use those passed as parameters.
        """

    def use(
        self,
        module: Module,
        *,
        priority: Priority | PriorityStr = ...,
    ) -> Self:
        """
        Function for using another module. Using another module replaces the module's
        dependencies with those of the module used. If the dependency is not found, it
        will be searched for in the module's dependency container.
        """

    def stop_using(self, module: Module) -> Self:
        """
        Function to remove a module in use.
        """

    @contextmanager
    def use_temporarily(
        self,
        module: Module,
        *,
        priority: Priority | PriorityStr = ...,
    ) -> Iterator[None]:
        """
        Context manager or decorator for temporary use of a module.
        """

    def change_priority(
        self,
        module: Module,
        priority: Priority | PriorityStr,
    ) -> Self:
        """
        Function for changing the priority of a module in use.
        There are two priority values:

        * **LOW**: The module concerned becomes the least important of the modules used.
        * **HIGH**: The module concerned becomes the most important of the modules used.
        """

    def unlock(self) -> Self:
        """
        Function to unlock the module by deleting cached instances of singletons.
        """

    async def all_ready(self) -> None: ...
    def add_logger(self, logger: Logger) -> Self: ...
    @classmethod
    def from_name(cls, name: str) -> Module:
        """
        Class method for getting or creating a module by name.
        """

    @classmethod
    def default(cls) -> Module:
        """
        Class method for getting the default module.
        """

@final
class Mode(Enum):
    FALLBACK = ...
    NORMAL = ...
    OVERRIDE = ...

@final
class Priority(Enum):
    LOW = ...
    HIGH = ...
