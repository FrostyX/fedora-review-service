from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import Bugzilla
from fedora_review_service.templates import (
    BugzillaComment,
    SponsorRequestIssue,
    SponsorRequestComment,
    SponsorRequestBugzilla,
)
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
            "https://github.com/FrostyX/fedora-review-service\n"
            "\n"
            "If you want to trigger a new Copr build, add a comment "
            "containing new\n"
            "Spec and SRPM URLs or [fedora-review-service-build] string."
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
            "https://github.com/FrostyX/fedora-review-service\n"
            "\n"
            "If you want to trigger a new Copr build, add a comment "
            "containing new\n"
            "Spec and SRPM URLs or [fedora-review-service-build] string."
        )
        copr = Copr(message)
        comment = BugzillaComment(copr).render()
        assert comment == expected

    # def test_render_different_spec(self):
    #     message = self.get_message("copr-review-build-end.json")
    #     expected = (
    #         "Copr build:\n"
    #         "https://copr.fedorainfracloud.org/coprs/build/5069760\n"
    #         "(succeeded)\n"
    #         "\n"
    #         "Error: Spec file as given by URL is not the same as in SRPM\n"
    #         "\n"
    #         "\n"
    #         "---\n"
    #         "This comment was created by the fedora-review-service\n"
    #         "https://github.com/FrostyX/fedora-review-service"
    #     )
    #     copr = Copr(message)
    #     comment = BugzillaComment(copr).render()
    #     assert comment == expected


class TestSponsorRequestIssue(MessageTestCase):
    def test_render(self):
        message = self.get_message("bugzilla-fedora-review-plus.json")
        expected = (
            "A Fedora Review ticket was approved and requires a sponsor.\n"
            "\n"
            "RHBZ: [2158000](https://bugzilla.redhat.com/show_bug.cgi?id=2158000)"
            "\n"
            "Package: light - Control backlight controllers\n"
            "Contributor: Jakub Kadlčík (FAS @user1)\n"
            "Reviewer: Jakub Kadlčík\n"
            "\n"
            "---\n"
            "This ticket was created by the fedora-review-service\n"
            "https://github.com/FrostyX/fedora-review-service"
        )
        bz = Bugzilla(message)
        comment = SponsorRequestIssue(bz, "user1").render()
        assert comment == expected


class TestSponsorRequestComment(MessageTestCase):
    def test_render(self):
        message = self.get_message("bugzilla-fedora-review-plus.json")
        expected = (
            "Hello @user1,\n"
            "please let us know if you already found a sponsor somewhere "
            "else. In\nsuch case we can assign the correct person to this "
            "ticket and not\ninterfere with their process.\n"
            "\n"
            "Feel free take this opportunity to also say a few words about\n"
            "yourself. It is not mandatory so you don't have to, but it will "
            "help\nus form a human connection."
        )
        bz = Bugzilla(message)
        comment = SponsorRequestComment(bz, "user1").render()
        assert comment == expected


class TestSponsorRequestBugzilla(MessageTestCase):
    def test_render(self):
        message = self.get_message("bugzilla-fedora-review-plus.json")
        expected = (
            "Hello @user1,\n"
            "since this is your first Fedora package, you need to get sponsored by a package\n"
            "sponsor before it can be accepted.\n"
            "\n"
            "A sponsor is an experienced package maintainer who will guide you through\n"
            "the processes that you will follow and the tools that you will use as a future\n"
            "maintainer. A sponsor will also be there to answer your questions related to\n"
            "packaging.\n"
            "\n"
            "You can find all active sponsors here:\n"
            "https://docs.pagure.org/fedora-sponsors/\n"
            "\n"
            "I created a sponsorship request for you:\n"
            "http://pagure.example/foo/bar/3\n"
            "Please take a look and make sure the information is correct.\n"
            "\n"
            "Thank you, and best of luck on your packaging journey.\n"
            "\n"
            "---\n"
            "This comment was created by the fedora-review-service\n"
            "https://github.com/FrostyX/fedora-review-service"
        )
        bz = Bugzilla(message)
        url = "http://pagure.example/foo/bar/3"
        comment = SponsorRequestBugzilla(bz, "user1", url).render()
        assert comment == expected
