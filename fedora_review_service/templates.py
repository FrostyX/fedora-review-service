import jinja2
from fedora_review_service.helpers import fas_url


class Template:
    def _render_template(self, path, values):
        loader = jinja2.FileSystemLoader("./templates")
        env = jinja2.Environment(loader=loader)

        # For some reason, lstrip_blocks doesn't work
        env.trim_blocks = True
        env.lstrip_blocks = True

        template = env.get_template(path)
        return template.render(**values)


class BugzillaComment(Template):

    def __init__(self, copr_message, review_report=None):
        self.message = copr_message
        self.report = review_report

    def render(self):
        path = "bugzilla-comment.j2"
        values = {
            "build_url": self.message.build_url,
            "build_status": self.message.status_text,
            "review_template_url": self.message.review_template_url,
            "builder_live_log_url": self.message.builder_live_log_url,
            "issues": self.issues,
        }
        return self._render_template(path, values)

    @property
    def issues(self):
        # Parse issues and [!] checkboxes from review.json once the JSON
        # support for fedora-review is merged and released
        # https://pagure.io/FedoraReview/pull-request/463
        return []


class SponsorRequestIssue(Template):
    def __init__(self, message, fas):
        self.message = message
        self.fas = fas

    def render(self):
        path = "sponsor-request-issue.j2"
        values = {
            "rhbz": self.message.id,
            "url": self.message.bug["weburl"],
            "summary": self.message.bug["summary"].lstrip("Review Request:"),
            "contributor": self.message.bug["reporter"]["real_name"],
            "reviewer": self.message.event["user"]["real_name"],
            "fas": self.fas,
        }
        return self._render_template(path, values)


class SponsorRequestComment(Template):
    def __init__(self, message, fas):
        self.message = message
        self.fas = fas

    def render(self):
        path = "sponsor-request-comment.j2"
        values = {"fas": self.fas}
        return self._render_template(path, values)


class SponsorRequestBugzilla(Template):
    def __init__(self, message, fas, sponsorship_request_url):
        self.message = message
        self.fas = fas
        self.sponsorship_request_url = sponsorship_request_url

    def render(self):
        path = "sponsor-request-bugzilla.j2"
        values = {
            "fas": self.fas,
            "sponsorship_request_url": self.sponsorship_request_url,
        }
        return self._render_template(path, values)
