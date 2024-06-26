from fedora_review_service.helpers import find_srpm_url, review_package_name
from fedora_review_service.config import config
from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import (
    Bugzilla,
    recognize,
    ReviewTicketCreated,
    CommentWithSRPM,
    ManualTrigger,
    FedoraReviewPlus,
)
from tests.base import MessageTestCase


class TestCopr(MessageTestCase):

    def test_ignore(self):
        name = "copr-review-build-end.json"

        message = self.get_message(name)
        assert Copr(message).ignore is False

        message = self.get_message(name)
        message.body["chroot"] = "fedora-37-x86_64"
        assert Copr(message).ignore is True

        message = self.get_message(name)
        message.body["owner"] = "jdoe"
        assert Copr(message).ignore is True

        message = self.get_message(name)
        message.body["copr"] = "coprname-not-related-to-review"
        assert Copr(message).ignore is True

    def test_failed_srpm(self):
        config["copr_owner"] = "frostyx"
        message = self.get_message("copr-build-srpm-fail.json")
        assert Copr(message).ignore is False


class TestBugzilla(MessageTestCase):

    def test_ignore(self):
        message = self.get_message("bugzilla-contributor-srpm-update.json")
        assert Bugzilla(message).ignore is False
        assert isinstance(recognize(message), CommentWithSRPM)

        message = self.get_message("bugzilla-reviewer-comment.json")
        assert Bugzilla(message).ignore is False
        assert recognize(message) is None

        message = self.get_message("bugzilla-reviewer-metadata-update.json")
        assert Bugzilla(message).ignore is False
        assert recognize(message) is None

        # A request to manually trigger a new build
        message = self.get_message("fedora-review-service-build.json")
        assert Bugzilla(message).ignore is False
        assert isinstance(recognize(message), ManualTrigger)

        # A comment from the fedora-review-service itself, containg the
        # [fedora-review-service-build] string
        message = self.get_message("fedora-review-service-build-ignore.json")
        assert Bugzilla(message).ignore is False
        assert recognize(message) is None

        message = self.get_message("case-sensitivity.json")
        assert Bugzilla(message).ignore is False
        assert isinstance(recognize(message), ReviewTicketCreated)

        message = self.get_message("bugzilla-fedora-review-plus.json")
        assert Bugzilla(message).ignore is False
        assert isinstance(recognize(message), FedoraReviewPlus)

        message = self.get_message("bugzilla-fedora-review-questionmark.json")
        assert Bugzilla(message).ignore is False
        assert recognize(message) is None

        message = self.get_message("bugzilla-invalid-summary.json")
        assert Bugzilla(message).ignore is False
        assert isinstance(recognize(message), ReviewTicketCreated)

    def test_find_srpm_url(self):
        message = self.get_message("bugzilla-contributor-srpm-update.json")
        packagename = review_package_name(message.body["bug"]["summary"])
        srpm_url = find_srpm_url(packagename, message.body["comment"]["body"])
        assert srpm_url == (
            "https://download.copr.fedorainfracloud.org"
            "/results/aleasto/waydroid/fedora-rawhide-x86_64/05068987-libgbinder"
            "/libgbinder-1.1.29-1.fc38.src.rpm"
        )

    def test_find_srpm_url_rhbz_2276411(self):
        message = self.get_message("bugzilla-case-sensitive-srpm-url.json")
        packagename = review_package_name(message.body["bug"]["summary"])
        srpm_url = find_srpm_url(packagename, message.body["comment"]["body"])
        assert srpm_url == (
            "https://download.copr.fedorainfracloud.org"
            "/results/mavit/perlimports/fedora-rawhide-x86_64/"
            "07334170-perl-File-XDG/perl-File-XDG-1.02-1.fc41.src.rpm"
        )
