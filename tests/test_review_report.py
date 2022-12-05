import os
import unittest

from fedora_review_service.review_report import ReviewReport


class TestReviewReport(unittest.TestCase):

    def setUp(self):
        self.here = os.path.dirname(os.path.abspath(__file__))
        self.data = os.path.join(self.here, "data")

    def get_report(self, name):
        path = os.path.join(self.data, name)
        return ReviewReport.from_file(path)

    def test_count(self):
        report = self.get_report("review-1.json")
        assert report.count("pending") == 34
        assert report.count("pass") == 35
        assert report.count("fail") == 2
