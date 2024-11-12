from uuid import UUID

from injection import LazyInstance

from ...sources.services.uuid_service import UUIDService


class TestUUIDService:
    uuid_service = LazyInstance(UUIDService)

    def test_generate_with_success_return_uuid(self):
        uuid = self.uuid_service.generate()

        assert isinstance(uuid, UUID)
