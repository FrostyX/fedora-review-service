from fedora_review_service.messages.copr import Copr
from fedora_review_service.bugzilla_comment import BugzillaComment
from tests.base import MessageTestCase


class TestBugzillaComment(MessageTestCase):

    def test_render(self):
        message = self.get_message("copr-review-build-end.json")
        expected = (
            "Copr build:\n"
            "https://copr.fedorainfracloud.org/coprs/build/5069760\n"
            "(succeeded)\n"
            "\n"
            "Review template:\n"
            "https://download.copr.fedorainfracloud.org/results/frostyx/"
            "fedora-review-2120131-libgbinder/fedora-rawhide-x86_64/"
            "05069760-libgbinder/fedora-review/review.txt\n"
            "\n"
            "Please take a look if any issues were found."
            "\n"
            "\n"
            "---\n"
            "This comment was created by the fedora-review-service\n"
            "https://github.com/FrostyX/fedora-review-service"
        )
        copr = Copr(message)
        comment = BugzillaComment(copr).render()
        assert comment == expected

    def test_render_build_fail(self):
        message = self.get_message("copr-review-build-fail.json")
        expected = (
            "Copr build:\n"
            "https://copr.fedorainfracloud.org/coprs/build/5074449\n"
            "(failed)\n"
            "\n"
            "Build log:\n"
            "https://download.copr.fedorainfracloud.org/results/frostyx/"
            "fedora-review-2009155-python-oslo-messaging/fedora-rawhide-x86_64/"
            "05074449-python-oslo-messaging/builder-live.log.gz\n"
            "\n"
            "Please make sure the package builds successfully at least for "
            "Fedora Rawhide.\n"
            "\n"
            "- If the build failed for unrelated reasons (e.g. temporary "
            "network\n  unavailability), please ignore it.\n"
            "- If the build failed because of missing BuildRequires, please "
            "make sure they\n  are listed in the \"Depends On\" field\n"
            "\n"
            "\n"
            "---\n"
            "This comment was created by the fedora-review-service\n"
            "https://github.com/FrostyX/fedora-review-service"
        )
        copr = Copr(message)
        comment = BugzillaComment(copr).render()
        assert comment == expected
