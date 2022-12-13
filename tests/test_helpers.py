from fedora_review_service.helpers import review_package_name, diff
from tests.base import MessageTestCase


class TestHelpers(MessageTestCase):

    def test_review_package_name(self):
        summary = "Review Request: libgbinder - C interfaces for Android binder"
        assert review_package_name(summary) == "libgbinder"

    def test_diff(self):
        with open("tests/data/oneapi-level-zero-05117233.spec") as fp:
            text1 = fp.read()

        with open("tests/data/oneapi-level-zero-05117358.spec") as fp:
            text2 = fp.read()

        with open("tests/data/oneapi-level-zero.diff") as fp:
            expected = fp.read()

        # The is some whitespace difference that we don't care about, so we
        # can't simply do `assert result == expected`
        result = diff(text1, text2)
        for (line1, line2) in zip(result.split("\n"), expected.split("\n")):
            line1.strip() == line2.strip()
