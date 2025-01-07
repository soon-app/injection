from collections.abc import Awaitable
from types import GenericAlias
from typing import Any, TypeAliasType

from injection import Module, mod
from injection.exceptions import InjectionError
from injection.integrations import _is_installed

__all__ = ("Inject",)

if _is_installed("fastapi", __name__):
    from fastapi import Depends


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
        instance = await self.__lazy_instance

        if instance is NotImplemented:
            raise InjectionError(f"`{self.__class}` is an unknown dependency.")

        return instance

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.__key == other.__key

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__key)

    @property
    def __key(self) -> tuple[type[T] | TypeAliasType | GenericAlias, Module]:
        return self.__class, self.__module
