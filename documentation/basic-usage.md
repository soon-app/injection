# Basic usage

## Register an injectable

> **Note**: If the class needs dependencies, these will be resolved when the instance is retrieved.

If you wish to inject a singleton, use `singleton` decorator.

```python
from injection import singleton

@singleton
class ServiceA:
    """ class implementation """
```

If you wish to inject a new instance each time, use `injectable` decorator.

```python
from injection import injectable

@injectable
class ServiceB:
    """ class implementation """
```

If you have a constant (such as a global variable) and wish to register it as an injectable, use `set_constant`
function.

```python
from injection import set_constant

class ServiceC:
    """ class implementation """

service_c = ServiceC()
set_constant(service_c)
```

Or here is the decorator `constant` which is equivalent:

> Unlike `@singleton`, dependencies will not be resolved.

```python
from injection import constant

@constant
class ServiceC:
    """ class implementation """
```

## Inject an instance

To inject one or several instances, use `inject` decorator.
_Don't forget to annotate type of parameter to inject._

```python
from injection import inject

@inject
def some_function(service_a: ServiceA):
    """ function implementation """
```

If `inject` decorates a class, it will be applied to the `__init__` method.
_Especially useful for dataclasses:_

> **Note**: Doesn't work with Pydantic `BaseModel` because the signature of the `__init__` method doesn't contain the
> dependencies.

```python
from dataclasses import dataclass

from injection import inject

@inject
@dataclass
class SomeDataClass:
    service_a: ServiceA = ...
```

### Threadsafe injection

With `threadsafe=True`, the injection logic is wrapped in a `threading.Lock`.

```python
@inject(threadsafe=True)
def some_function(service_a: ServiceA):
    """ function implementation """
```

## Get an instance

_Example with `get_instance` function:_

```python
from injection import get_instance

service_a = get_instance(ServiceA)
```

_Example with `aget_instance` function:_

```python
from injection import aget_instance

service_a = await aget_instance(ServiceA)
```

_Example with `get_lazy_instance` function:_

```python
from injection import get_lazy_instance

lazy_service_a = get_lazy_instance(ServiceA)
# ...
service_a = ~lazy_service_a
```

_Example with `aget_lazy_instance` function:_

```python
from injection import aget_lazy_instance

lazy_service_a = aget_lazy_instance(ServiceA)
# ...
service_a = await lazy_service_a
```

## Inheritance

In the case of inheritance, you can use the decorator parameter `on` to link the injection to one or several other
classes.

**Warning: if the child class is in another file, make sure that file is imported before injection.**
[_See `load_packages` function._](utils.md#load_packages)

_Example with one class:_

```python
class AbstractService(ABC):
    ...

@injectable(on=AbstractService)
class ConcreteService(AbstractService):
    ...
```

_Example with several classes:_

```python
class AbstractService(ABC):
    ...

class ConcreteService(AbstractService):
    ...

@injectable(on=(AbstractService, ConcreteService))
class ConcreteServiceOverload(ConcreteService):
    ...
```

If a class is registered in a package, and you want to override it, there is the `mode` parameter:

```python
@injectable
class InaccessibleService:
    ...

# ...

@injectable(on=InaccessibleService, mode="override")
class ServiceOverload(InaccessibleService):
    ...
```

## Recipes

A recipe is a function that tells the injector how to construct the instance to be injected. It is important to specify 
the return type annotation when defining the recipe.

```python
from injection import injectable

@injectable
def service_d_recipe() -> ServiceD:
    """ recipe implementation """
```

### Async recipes

An asynchronous recipe is defined in the same way as a conventional recipe. To retrieve an instance of an asynchronous
recipe, you need to be in an asynchronous context (decorate an asynchronous function with `@inject` or use an
asynchronous getter).

Asynchronous singletons can be retrieved in a synchronous context if they have already been instantiated. The
`all_ready` method ensures that all singletons have been instantiated.

```python
from injection import get_instance, mod, singleton

@singleton
async def service_e_recipe() -> ServiceE:
    """ recipe implementation """

async def main():
    await mod().all_ready()
    # ...
    service_e = get_instance(ServiceE)
```

## Working with type aliases

```python
from injection import injectable, set_constant

type APIKey = str

set_constant("<secret_api_key>", APIKey, alias=True)

@injectable
class Client:
    def __init__(self, api_key: APIKey):
        ...
```
