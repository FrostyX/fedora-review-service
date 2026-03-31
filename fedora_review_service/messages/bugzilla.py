from fedora_messaging import message as review_message
from fedora_review_service.helpers import (
    review_package_name,
    find_srpm_url,
    find_spec_url,
)


class Bugzilla:

    def __init__(self, message):
        self.message = message
        self.event = message.body["event"]
        self.bug = message.body["bug"]
        self.id = self.bug["id"]
        self.comment = message.body.get("comment")

    @property
    def packagename(self):
        return review_package_name(self.bug["summary"])

    @property
    def owner(self):
        return self.bug["reporter"]["login"]

    @property
    def srpm_url(self):
        return find_srpm_url(self.packagename, self.comment["body"])

    @property
    def spec_url(self):
        return find_spec_url(self.packagename, self.comment["body"])

    @property
    def ignore(self):
        return (
            self.bug["component"] != "Package Review"
            or should_ignore(message=self.message)
        )


def should_ignore(message: review_message.Message) -> bool:
    """
    Check for keywords to ignore review service builds

    True if keywords found, False otherwise.
    """
    ignore_keyword: str = "[fedora-review-service-ignore]"
    return (
        (
            message.body.get("comment") is not None
            and ignore_keyword in message.body.get("comment")["body"]
        )
        or ignore_keyword in message.body["bug"]["keywords"]
        or ignore_keyword in message.body["bug"]["whiteboard"]
    )


def recognize(message):
    """
    Recognize a specific bugzilla message
    """
    if Bugzilla(message).ignore:
        return None

    classes = [
        ReviewTicketCreated,
        CommentWithSRPM,
        ManualTrigger,
        FedoraReviewPlus,
    ]
    for clazz in classes:
        bz = clazz(message)
        if bz.recognized:
            return bz
    return None


class ReviewTicketCreated(Bugzilla):
    """
    """
    @property
    def recognized(self):
        if not self.comment:
            return False
        return self.comment["number"] == 0


class CommentWithSRPM(Bugzilla):
    """
    New SRPM URL submitted by the contributor
    """
    @property
    def recognized(self):
        if not self.comment:
            return False
        if self.bug["reporter"]["login"] != self.comment["author"]:
            return False
        return bool(self.srpm_url)


class ManualTrigger(Bugzilla):
    """
    A comment triggering a manual Copr rebuild
    """
    @property
    def recognized(self):
        if not self.comment:
            return False

        # We need to ignore comments from the fedora-review-service itself
        # otherwise we will end up in an infinite loop
        text = "---\nThis comment was created by the fedora-review-service"
        if text in self.comment["body"]:
            return False
        return "[fedora-review-service-build]" in self.comment["body"]


class FedoraReviewPlus(Bugzilla):
    """
    The Bugzilla ticket just got fedora-review+ flag
    """
    @property
    def recognized(self):
        if self.event.get("action") != "modify":
            return False

        for change in self.event.get("changes", []):
            if change["field"] != "flag.fedora-review":
                continue
            if change["added"] != "+":
                continue
            return True

        return False
