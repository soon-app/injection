import sys

from injection.utils import load_modules_with_keywords


class TestLoadModulesWithKeywords:
    def test_load_modules_with_keywords_with_success(self):
        from tests.utils import package2

        loaded_modules = load_modules_with_keywords(package2)
        assert len(loaded_modules) == 1
        assert "tests.utils.package2.sub_package.injectable" in loaded_modules
        assert "tests.utils.package2.sub_package.injectable" in sys.modules
        assert "tests.utils.package2.module" not in sys.modules
