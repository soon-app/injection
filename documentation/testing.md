# Testing

## Test configuration

Here is the [Pytest](https://github.com/pytest-dev/pytest) fixture for using test injectables on all tests:

```python
# conftest.py

import pytest
from injection.testing import load_test_profile

@pytest.fixture(scope="session", autouse=True)
def autouse_test_injectables():
    # Ensure that test injectables have been imported here

    with load_test_profile():
        yield
```

## Register a test injectable

> **Notes**
> * Test injectables replace conventional injectables if they are registered on the same type.
> * A test injectable can't depend on a conventional injectable.

`@singleton` equivalent for testing:


```python
from injection.testing import test_singleton

@test_singleton
class ServiceA:
    """ class implementation """
```

`@injectable` equivalent for testing:


```python
from injection.testing import test_injectable

@test_injectable
class ServiceB:
    """ class implementation """
```

`set_constant` equivalent for testing:

```python
from injection.testing import set_test_constant

class ServiceC:
    """ class implementation """

service_c = ServiceC()
set_test_constant(service_c)
```

## Writing test classes

With Pytest, it's not possible to implement the `__init__` method of a test class, which makes retrieving dependencies 
a little more complicated.
The solution provided by this package is based on a descriptor `LazyInstance`.
Each time the descriptor is accessed with `self`, the dependency is resolved. So **be careful** with `@injectable`, if you 
want to keep its state, assign it to a variable.

Here's an example:

```python
from injection import LazyInstance

class TestSomething:
    dependency = LazyInstance(DependencyClass)

    def test_something(self):
        # ...
        self.dependency.do_work()
        # ...
```