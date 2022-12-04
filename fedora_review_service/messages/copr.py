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

    @property
    def ignore(self):
        # TODO We should also care about srpm-builds that failed
        # so that we can link the SRPM builder-live.log.gz
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
