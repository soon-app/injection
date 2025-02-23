from typing import ContextManager, Final

from injection import Module

__MODULE: Final[Module] = ...

set_test_constant = __MODULE.set_constant
should_be_test_injectable = __MODULE.should_be_injectable
test_constant = __MODULE.constant
test_injectable = __MODULE.injectable
test_scoped = __MODULE.scoped
test_singleton = __MODULE.singleton

def load_test_profile(*names: str) -> ContextManager[Module]:
    """
    Context manager or decorator for temporary use test module.
    """
