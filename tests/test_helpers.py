from fedora_review_service.helpers import (
    review_package_name,
    diff,
    find_fas_username,
)
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

    def test_find_fas_username(self):
        text = ("Spec URL: https://example/foo.spec\n"
                "SRPM URL: https://example/foo-1.0.fc33.src.rpm\n"
                "\n"
                "Description:\n"
                "Some multiline description\nand so on\n"
                "\n{0}\n"
                "And maybe some additional text")

        # This is all the variants that I found in tickets
        fas_lines = [
            "Fedora Account System Username: frostyx",
            "Fedora Account System Username:frostyx",
            "Fedora Account System Username: \nfrostyx",
            "Fedora Account System Username:\nfrostyx",
            "Fedora Account System Username:\n  frostyx",
        ]
        for fas_line in fas_lines:
            comment = text.format(fas_line)
            assert find_fas_username(comment) == "frostyx"

        # False-positives like this are not ideal, we would rather return `None`.
        # It is not a problem because we will query the user to verify the
        # username. But feel free to fix this.
        comment = text.format("Fedora Account System Username:")
        assert find_fas_username(comment) == "And"
