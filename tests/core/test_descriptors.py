from injection import LazyInstance, injectable


class TestLazyInstance:
    def test_lazy_instance_with_instance_return_t(self):
        @injectable
        class Dependency: ...

        class SomeClass:
            dependency = LazyInstance(Dependency)

        instance = SomeClass()
        assert isinstance(instance.dependency, Dependency)

    def test_lazy_instance_with_class_return_self(self):
        @injectable
        class Dependency: ...

        descriptor = LazyInstance(Dependency)

        class SomeClass:
            dependency = descriptor

        assert SomeClass.dependency is descriptor

    def test_lazy_instance_with_undefined_dependency_return_not_implemented(self):
        class UndefinedDependency: ...

        class SomeClass:
            dependency = LazyInstance(UndefinedDependency)

        instance = SomeClass()
        assert instance.dependency is NotImplemented
