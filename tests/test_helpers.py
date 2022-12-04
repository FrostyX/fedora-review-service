from fedora_review_service.helpers import review_package_name
from tests.base import MessageTestCase


class TestHelpers(MessageTestCase):

    def test_review_package_name(self):
        summary = "Review Request: libgbinder - C interfaces for Android binder"
        assert review_package_name(summary) == "libgbinder"
