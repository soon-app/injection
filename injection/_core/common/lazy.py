from collections.abc import Callable, Iterator, Mapping
from types import MappingProxyType

from injection._core.common.invertible import Invertible


class Lazy[T](Invertible[T]):
    __slots__ = ("__iterator", "__is_set")

    __iterator: Iterator[T]
    __is_set: bool

    def __init__(self, factory: Callable[..., T]) -> None:
        self.__setup_cache(factory)

    def __invert__(self) -> T:
        return next(self.__iterator)

    @property
    def is_set(self) -> bool:
        return self.__is_set

    def __setup_cache(self, factory: Callable[..., T]) -> None:
        def infinite_yield() -> Iterator[T]:
            nonlocal factory
            cached = factory()
            self.__is_set = True
            del factory

            while True:
                yield cached

        self.__iterator = infinite_yield()
        self.__is_set = False


class LazyMapping[K, V](Mapping[K, V]):
    __slots__ = ("__lazy",)

    __lazy: Lazy[Mapping[K, V]]

    def __init__(self, iterator: Iterator[tuple[K, V]]) -> None:
        self.__lazy = Lazy(lambda: MappingProxyType(dict(iterator)))

    def __getitem__(self, key: K, /) -> V:
        return (~self.__lazy)[key]

    def __iter__(self) -> Iterator[K]:
        yield from ~self.__lazy

    def __len__(self) -> int:
        return len(~self.__lazy)

    @property
    def is_set(self) -> bool:
        return self.__lazy.is_set
