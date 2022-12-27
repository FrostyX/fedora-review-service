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

        if self.bug["reporter"]["login"] != self.comment["author"]:
            return True

        # TODO If not already closed
        # {'id': 1, 'name': 'NEW'}
        self.bug["status"]

        # TODO If not already fedora-review+
        self.bug["flags"]

        if not self.srpm_url:
            return True
        return False
