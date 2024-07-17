from typing import Any, override

from rodi import ContainerProtocol

from injection import Module, mod

__all__ = ("InjectionServices",)


class InjectionServices(ContainerProtocol):
    """
    BlackSheep dependency injection container implemented with `python-injection`.
    """

    __slots__ = ("__module",)

    def __init__(self, module: Module = None):
        self.__module = module or mod()

    @override
    def __contains__(self, item: Any) -> bool:
        return item in self.__module

    @override
    def register(self, obj_type: type | Any, *args, **kwargs):
        self.__module.injectable(obj_type)

    @override
    def resolve[T](self, obj_type: type[T] | Any, *args, **kwargs) -> T:
        return self.__module.find_instance(obj_type)
