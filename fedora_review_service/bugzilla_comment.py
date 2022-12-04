import jinja2


class BugzillaComment:

    def __init__(self, copr_message, review_report=None):
        self.message = copr_message
        self.report = review_report

    def render(self):
        loader = jinja2.FileSystemLoader(".")
        env = jinja2.Environment(loader=loader)

        # For some reason, lstrip_blocks doesn't work
        env.trim_blocks = True
        env.lstrip_blocks = True

        template = env.get_template("bugzilla-comment.j2")
        values = {
            "build_url": self.message.build_url,
            "build_status": self.message.status_text,
            "review_template_url": self.message.review_template_url,
            "builder_live_log_url": self.message.builder_live_log_url,
            "issues": self.issues,
        }
        return template.render(**values)

    @property
    def issues(self):
        # Parse issues and [!] checkboxes from review.json once the JSON
        # support for fedora-review is merged and released
        # https://pagure.io/FedoraReview/pull-request/463
        return []
