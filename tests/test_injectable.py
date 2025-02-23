from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from injection import aget_instance, get_instance, injectable


class TestInjectable:
    def test_injectable_with_success(self):
        @injectable
        class SomeInjectable: ...

        instance_1 = get_instance(SomeInjectable)
        instance_2 = get_instance(SomeInjectable)
        assert instance_1 is not instance_2

    def test_injectable_with_recipe(self):
        class SomeClass: ...

        @injectable
        def recipe() -> SomeClass:
            return SomeClass()

        instance_1 = get_instance(SomeClass)
        instance_2 = get_instance(SomeClass)
        assert instance_1 is not instance_2

    async def test_injectable_with_async_recipe(self):
        class SomeClass: ...

        @injectable
        async def recipe() -> SomeClass:
            return SomeClass()

        with pytest.raises(RuntimeError):
            get_instance(SomeClass)

        instance_1 = await aget_instance(SomeClass)
        instance_2 = await aget_instance(SomeClass)
        assert instance_1 is not instance_2

    def test_injectable_with_recipe_and_union(self):
        class A: ...

        class B(A): ...

        @injectable
        def recipe() -> A | B:
            return B()

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, B)
        assert isinstance(b, B)
        assert a is not get_instance(A)
        assert b is not get_instance(B)

    def test_injectable_with_recipe_and_no_return_type(self):
        class SomeClass: ...

        @injectable
        def recipe():
            return SomeClass()  # pragma: no cover

        assert get_instance(SomeClass) is None

    def test_injectable_with_on(self):
        class A: ...

        @injectable(on=A)
        class B(A): ...

        a = get_instance(A)
        assert isinstance(a, B)

    def test_injectable_with_on_and_several_classes(self):
        class A: ...

        class B(A): ...

        @injectable(on=(A, B))
        class C(B): ...

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, C)
        assert isinstance(b, C)
        assert a is not b

    def test_injectable_with_inject(self):
        @injectable
        class A: ...

        @injectable
        class B:
            def __init__(self, __a: A):
                self.a = __a

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, A)
        assert isinstance(b, B)
        assert isinstance(b.a, A)
        assert a is not b.a

    def test_injectable_with_dataclass_and_inject(self):
        @injectable
        class A: ...

        @injectable
        @dataclass(frozen=True, slots=True)
        class B:
            a: A

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, A)
        assert isinstance(b, B)
        assert isinstance(b.a, A)
        assert a is not b.a

    def test_injectable_with_pydantic_model_and_inject(self):
        @injectable
        class A(BaseModel): ...

        @injectable
        class B(BaseModel):
            a: A

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, A)
        assert isinstance(b, B)
        assert isinstance(b.a, A)
        assert a is not b.a

    def test_injectable_with_recipe_and_inject(self):
        @injectable
        class A: ...

        class B: ...

        @injectable
        def recipe(__a: A) -> B:
            assert isinstance(__a, A)
            assert __a is not a
            return B()

        a = get_instance(A)
        b = get_instance(B)
        assert isinstance(a, A)
        assert isinstance(b, B)

    def test_injectable_with_injectable_already_exist_raise_runtime_error(self):
        class A: ...

        @injectable(on=A)
        class B(A): ...

        with pytest.raises(RuntimeError):

            @injectable(on=A)
            class C(A): ...

    def test_injectable_with_override(self):
        @injectable
        class A: ...

        @injectable(on=A, mode="override")
        class B(A): ...

        a = get_instance(A)
        assert isinstance(a, B)

    def test_injectable_with_multiple_override(self):
        @injectable
        class A: ...

        @injectable(on=A, mode="override")
        class B(A): ...

        @injectable(on=A, mode="override")
        class C(B): ...

        a = get_instance(A)
        assert isinstance(a, C)

    def test_injectable_with_class_and_update_method(self):
        @injectable
        class A:
            def update(self):
                raise NotImplementedError

        a = get_instance(A)
        assert isinstance(a, A)
