import jinja2


class Copr:

    def __init__(self, message):
        self.message = message
        self.build_id = message.body["build"]
        self.chroot = message.body["chroot"]
        self.status = message.body["status"]
        self.ownername = message.body["owner"]
        self.projectname = message.body["copr"]
        self.packagename = message.body["pkg"]

    @property
    def fullname(self):
        return "{0}/{1}".format(self.ownername, self.projectname)

    @property
    def build_url(self):
        url = "https://copr.fedorainfracloud.org/coprs/build/{0}"
        return url.format(self.build_id)

    @property
    def review_template_url(self):
        return "{0}/{1}".format(self.destdir_url, "fedora-review/review.txt")

    @property
    def builder_live_log_url(self):
        return "{0}/{1}".format(self.destdir_url, "builder-live.log.gz")

    @property
    def destdir_url(self):
        base = "https://download.copr.fedorainfracloud.org/results"
        destdir = f"{self.build_id:08d}-{self.packagename}"
        return f"{base}/{self.fullname}/{self.chroot}/{destdir}"

    @property
    def status_text(self):
        return "failed" if self.status == 0 else "succeeded"

    @property
    def issues(self):
        # Parse issues and [!] checkboxes from review.json once the JSON
        # support for fedora-review is merged and released
        # https://pagure.io/FedoraReview/pull-request/463
        return []

    @property
    def rhbz_number(self):
        """
        We should instead have a database mapping BUILD_ID to RHBZ_ID
        but that's too much work for a prototype
        """
        split = self.projectname.split("-", 3)
        if len(split) < 4:
            return None
        if split[0] != "fedora" and split[1] != "review":
            return None
        if not split[2].isnumeric():
            return None
        return split[2]

    def render_bugzilla_comment(self):
        loader = jinja2.FileSystemLoader(".")
        env = jinja2.Environment(loader=loader)

        # For some reason, lstrip_blocks doesn't work
        env.trim_blocks = True
        env.lstrip_blocks = True

        template = env.get_template("bugzilla-comment.j2")
        values = {
            "build_url": self.build_url,
            "build_status": self.status_text,
            "review_template_url": self.review_template_url,
            "builder_live_log_url": self.builder_live_log_url,
            "issues": self.issues,
        }
        return template.render(**values)

    @property
    def ignore(self):
        if self.chroot != "fedora-rawhide-x86_64":
            return True

        # The build is still running, we want only the last chroot
        if self.status not in [0, 1]:
            return True

        if self.ownername != "frostyx":
            return True

        if not self.rhbz_number:
            return True
        return False
