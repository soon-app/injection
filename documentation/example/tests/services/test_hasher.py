from injection import LazyInstance

from ...sources.services.hasher import Argon2Hasher


class TestArgon2Hasher:
    hasher = LazyInstance(Argon2Hasher)

    def test_hash_with_success_return_str(self):
        value = "root"
        h = self.hasher.hash(value)

        assert h != value
        assert h.startswith("$argon2id$")
