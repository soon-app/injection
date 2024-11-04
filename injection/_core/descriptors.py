from typing import Self

from injection._core.common.invertible import Invertible
from injection._core.common.type import InputType
from injection._core.module import Module


class LazyInstance[T]:
    __slots__ = ("__value",)

    __value: Invertible[T]

    def __init__(self, cls: InputType[T], module: Module | None = None) -> None:
        module = module or Module.default()
        self.__value = module.get_lazy_instance(cls, default=NotImplemented)  # type: ignore[assignment]

    def __get__(
        self,
        instance: object | None = None,
        owner: type | None = None,
    ) -> Self | T:
        if instance is None:
            return self

        return ~self.__value
