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
        """
        Parse issues and [!] checkboxes from review.json
        """
        if not self.report or "issues" not in self.report:
            return []

        result = []
        for issue in self.report["issues"]:
            # There is also `issue["text"]` but that would be confusing to show
            # users. It is written as an explanation of what the check is doing
            # not as instructions what a user should do, e.g.
            #   "text": "Package does not use a name that already exists.",
            # When there is no note, rather print nothing.
            if not issue["note"]:
                continue

            item = "- {0}".format(issue["note"])
            if issue["url"]:
                item += "\n  Read more: {0}".format(issue["url"])
            result.append(item)
        return result


class SponsorRequestIssue(Template):
    def __init__(self, message, fas):
        self.message = message
        self.fas = fas

    @property
    def summary(self):
        right = self.message.bug["summary"].split("Review Request:")[-1]
        return right.strip()

    def render(self):
        path = "sponsor-request-issue.j2"
        values = {
            "rhbz": self.message.id,
            "url": self.message.bug["weburl"],
            "summary": self.summary,
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


class InvalidSummary(Template):
    def __init__(self, message):
        self.message = message

    def render(self):
        path = "invalid-summary.j2"
        values = {
            "summary": self.message.bug["summary"],
        }
        return self._render_template(path, values)


class MissingSRPM(Template):
    def __init__(self, message):
        self.message = message

    def render(self):
        path = "missing-srpm.j2"
        values = {}
        return self._render_template(path, values)


class FileNotAvailable(Template):
    def __init__(self, message, response, url_name):
        self.message = message
        self.response = response
        self.url_name = url_name

    def render(self):
        path = "file-not-available.j2"
        values = {
            "url_name": self.url_name,
            "response": self.response,
        }
        return self._render_template(path, values)
