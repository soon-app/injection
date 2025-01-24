from typing import ContextManager

from injection import Module

__module: Module = ...

set_test_constant = __module.set_constant
should_be_test_injectable = __module.should_be_injectable
test_constant = __module.constant
test_injectable = __module.injectable
test_singleton = __module.singleton

def load_test_profile(*names: str) -> ContextManager[None]:
    """
    Context manager or decorator for temporary use test module.
    """
