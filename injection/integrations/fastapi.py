from collections.abc import Callable
from types import GenericAlias
from typing import Any, ClassVar, Self, TypeAliasType

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
    __slots__ = ("__call__", "__class", "__module")

    __call__: Callable[[], T]
    __class: type[T] | TypeAliasType | GenericAlias
    __module: Module

    __sentinel: ClassVar[object] = object()

    def __init__(self, cls: type[T] | TypeAliasType | GenericAlias, module: Module):
        lazy_instance = module.get_lazy_instance(cls, default=self.__sentinel)
        self.__call__ = lambda: self.__ensure(~lazy_instance)
        self.__class = cls
        self.__module = module

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, type(self)):
            return self.__key == other.__key

        return NotImplemented

    def __hash__(self) -> int:
        return hash(self.__key)

    @property
    def __key(
        self,
    ) -> tuple[type[Self], type[T] | TypeAliasType | GenericAlias, Module]:
        return type(self), self.__class, self.__module

    def __ensure(self, instance: T | Any) -> T:
        if instance is self.__sentinel:
            raise InjectionError(f"`{self.__class}` is an unknown dependency.")

        return instance
