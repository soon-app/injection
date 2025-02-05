from collections.abc import Callable, Iterable, Iterator
from contextlib import contextmanager
from importlib import import_module
from importlib.util import find_spec
from pkgutil import walk_packages
from types import ModuleType as PythonModule
from typing import ContextManager

from injection import __name__ as injection_package_name
from injection import mod

__all__ = ("load_modules_with_keywords", "load_packages", "load_profile")


def load_profile(*names: str) -> ContextManager[None]:
    """
    Injection module initialization function based on profile name.
    A profile name is equivalent to an injection module name.
    """

    modules = tuple(mod(module_name) for module_name in names)

    for module in modules:
        module.unlock()

    target = mod().unlock().init_modules(*modules)

    del module, modules

    @contextmanager
    def cleaner() -> Iterator[None]:
        yield
        target.unlock().init_modules()

    return cleaner()


def load_modules_with_keywords(
    *packages: PythonModule | str,
    keywords: Iterable[str] | None = None,
) -> dict[str, PythonModule]:
    """
    Function to import modules from a Python package if one of the keywords is contained in the Python script.
    The default keywords are:
        - `from injection `
        - `from injection.`
        - `import injection`
    """

    if keywords is None:
        keywords = (
            f"from {injection_package_name} ",
            f"from {injection_package_name}.",
            f"import {injection_package_name}",
        )

    b_keywords = tuple(keyword.encode() for keyword in keywords)

    def predicate(module_name: str) -> bool:
        if (spec := find_spec(module_name)) and (module_path := spec.origin):
            with open(module_path, "rb") as script:
                for line in script:
                    line = b" ".join(line.split(b" ")).strip()

                    if line and any(keyword in line for keyword in b_keywords):
                        return True

        return False

    return load_packages(*packages, predicate=predicate)


def load_packages(
    *packages: PythonModule | str,
    predicate: Callable[[str], bool] = lambda module_name: True,
) -> dict[str, PythonModule]:
    """
    Function for importing all modules in a Python package.
    Pass the `predicate` parameter if you want to filter the modules to be imported.
    """

    loaded: dict[str, PythonModule] = {}

    for package in packages:
        if isinstance(package, str):
            package = import_module(package)

        loaded |= __iter_modules_from(package, predicate)

    return loaded


def __iter_modules_from(
    package: PythonModule,
    predicate: Callable[[str], bool],
) -> Iterator[tuple[str, PythonModule]]:
    package_name = package.__name__

    try:
        package_path = package.__path__
    except AttributeError as exc:
        raise TypeError(f"`{package_name}` isn't Python package.") from exc

    for info in walk_packages(path=package_path, prefix=f"{package_name}."):
        name = info.name

        if info.ispkg or not predicate(name):
            continue

        yield name, import_module(name)
