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
) -> Any:
    """
    Declare a FastAPI dependency with `python-injection`.
    """

    dependency: InjectionDependency[T] = InjectionDependency(cls, module or mod())
    return Depends(dependency, use_cache=False)


class InjectionDependency[T]:
    __slots__ = ("__awaitable",)

    __awaitable: Awaitable[T]

    def __init__(
        self,
        cls: type[T] | TypeAliasType | GenericAlias,
        module: Module,
    ) -> None:
        self.__awaitable = module.aget_lazy_instance(cls, default=NotImplemented)

    async def __call__(self) -> T:
        return await self.__awaitable
