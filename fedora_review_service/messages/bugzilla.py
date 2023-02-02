from fedora_review_service.helpers import (
    review_package_name,
    find_srpm_url,
    find_spec_url,
)


class Bugzilla:

    def __init__(self, message):
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
        if not self.bug["component"] == "Package Review":
            return True

        # Assignee update, CC update, flags update, etc
        if not self.comment:
            return True

        # New SRPM URL submitted by the contributor, don't ignore
        if self.is_new_srpm_build():
            return False

        # A comment triggering a manual Copr rebuild, don't ignore
        if self.is_manual_build_trigger():
            return False

        return True

    def is_new_srpm_build(self):
        if self.bug["reporter"]["login"] != self.comment["author"]:
            return False
        return bool(self.srpm_url)

    def is_manual_build_trigger(self):
        # We need to ignore comments from the fedora-review-service itself
        # otherwise we will end up in an infinite loop
        text = "---\nThis comment was created by the fedora-review-service"
        if text in self.comment["body"]:
            return False
        return "[fedora-review-service-build]" in self.comment["body"]
