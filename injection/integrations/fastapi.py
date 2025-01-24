from collections.abc import Awaitable
from types import GenericAlias
from typing import Any, TypeAliasType

from fastapi import Depends

from injection import Module, mod

__all__ = ("Inject",)


def Inject[T](  # noqa: N802
    cls: type[T] | TypeAliasType | GenericAlias,
    /,
    module: Module | None = None,
    *,
    scoped: bool = True,
) -> Any:
    """
    Declare a FastAPI dependency with `python-injection`.
    """

    dependency: InjectionDependency[T] = InjectionDependency(cls, module or mod())
    return Depends(dependency, use_cache=scoped)


class InjectionDependency[T]:
    __slots__ = ("__class", "__lazy_instance", "__module")

    __class: type[T] | TypeAliasType | GenericAlias
    __lazy_instance: Awaitable[T]
    __module: Module

    def __init__(
        self,
        cls: type[T] | TypeAliasType | GenericAlias,
        module: Module,
    ) -> None:
        self.__class = cls
        self.__lazy_instance = module.aget_lazy_instance(cls, default=NotImplemented)
        self.__module = module

    async def __call__(self) -> T:
        return await self.__lazy_instance

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.__key == other.__key

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__key)

    @property
    def __key(self) -> tuple[type[T] | TypeAliasType | GenericAlias, Module]:
        return self.__class, self.__module
