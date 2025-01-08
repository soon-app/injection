from abc import ABC, abstractmethod
from collections.abc import MutableMapping
from contextlib import suppress
from dataclasses import dataclass
from typing import Any, ClassVar, NoReturn, Protocol, runtime_checkable

from injection._core.common.asynchronous import Caller
from injection._core.common.threading import synchronized
from injection.exceptions import InjectionError


@runtime_checkable
class Injectable[T](Protocol):
    __slots__ = ()

    @property
    def is_locked(self) -> bool:
        return False

    def unlock(self) -> None:
        return

    @abstractmethod
    async def aget_instance(self) -> T:
        raise NotImplementedError

    @abstractmethod
    def get_instance(self) -> T:
        raise NotImplementedError


@dataclass(repr=False, frozen=True, slots=True)
class BaseInjectable[T](Injectable[T], ABC):
    factory: Caller[..., T]


class SimpleInjectable[T](BaseInjectable[T]):
    __slots__ = ()

    async def aget_instance(self) -> T:
        return await self.factory.acall()

    def get_instance(self) -> T:
        return self.factory.call()


class SingletonInjectable[T](BaseInjectable[T]):
    __slots__ = ("__dict__",)

    __key: ClassVar[str] = "$instance"

    @property
    def cache(self) -> MutableMapping[str, Any]:
        return self.__dict__

    @property
    def is_locked(self) -> bool:
        return self.__key in self.cache

    def unlock(self) -> None:
        self.cache.clear()

    async def aget_instance(self) -> T:
        with suppress(KeyError):
            return self.__check_instance()

        with synchronized():
            instance = await self.factory.acall()
            self.__set_instance(instance)

        return instance

    def get_instance(self) -> T:
        with suppress(KeyError):
            return self.__check_instance()

        with synchronized():
            instance = self.factory.call()
            self.__set_instance(instance)

        return instance

    def __check_instance(self) -> T:
        return self.cache[self.__key]

    def __set_instance(self, value: T) -> None:
        self.cache[self.__key] = value


@dataclass(repr=False, frozen=True, slots=True)
class ShouldBeInjectable[T](Injectable[T]):
    cls: type[T]

    async def aget_instance(self) -> T:
        return self.get_instance()

    def get_instance(self) -> NoReturn:
        raise InjectionError(f"`{self.cls}` should be an injectable.")
