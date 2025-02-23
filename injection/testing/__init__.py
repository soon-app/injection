from typing import ContextManager, Final

from injection import Module, mod
from injection.utils import load_profile

__all__ = (
    "load_test_profile",
    "set_test_constant",
    "should_be_test_injectable",
    "test_constant",
    "test_injectable",
    "test_scoped",
    "test_singleton",
)

_TEST_PROFILE_NAME: Final[str] = "__testing__"

set_test_constant = mod(_TEST_PROFILE_NAME).set_constant
should_be_test_injectable = mod(_TEST_PROFILE_NAME).should_be_injectable
test_constant = mod(_TEST_PROFILE_NAME).constant
test_injectable = mod(_TEST_PROFILE_NAME).injectable
test_scoped = mod(_TEST_PROFILE_NAME).scoped
test_singleton = mod(_TEST_PROFILE_NAME).singleton


def load_test_profile(*names: str) -> ContextManager[Module]:
    return load_profile(_TEST_PROFILE_NAME, *names)
