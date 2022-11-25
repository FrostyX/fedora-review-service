#!/usr/bin/python3

import jinja2
from fedora_messaging.api import consume
from fedora_messaging.config import conf


conf.setup_logging()


def consume(message):
    # If complicated, switch to class
    # https://fedora-messaging.readthedocs.io/en/latest/consuming.html#the-callback
    dispatch(message)


def dispatch(message):
    # FIXME It seems that this is called after every chroot ends
    if message.topic == "org.fedoraproject.prod.copr.build.end":
        return handle_copr_message(message)

    if False:
        return handle_bugzilla_messag(message)


def handle_copr_message(message):
    chroot = message.body["chroot"]
    if chroot != "fedora-rawhide-x86_64":
        return

    status = message.body["status"]
    if status not in [0, 1]:
        # The build is still running, we want only the last chroot
        return

    ownername = message.body["owner"]
    if ownername != "frostyx":
        return

    projectname = message.body["copr"]
    rhbz = rhbz_number(projectname)
    if not rhbz:
        return

    build_id = message.body["build"]
    status_text = "failed" if status == 0 else "succeeded"
    packagename = message.body["pkg"]

    build_url = get_build_url(build_id)
    review_template_url = get_review_template_url(
        build_id, ownername, projectname, packagename, chroot)

    # Parse issues and [!] checkboxes from review.json once the JSON
    # support for fedora-review is merged and released
    # https://pagure.io/FedoraReview/pull-request/463
    issues = ["First issue", "Second issue"]

    comment = render_bugzilla_comment(
        build_url,
        status_text,
        review_template_url,
        issues,
    )
    submit_bugzilla_comment(comment)


def handle_bugzilla_message(message):
    pass


def get_build_url(build_id):
    url = "https://copr.fedorainfracloud.org/coprs/build/{0}"
    return url.format(build_id)


def get_review_template_url(build_id, owner, project, package, chroot):
    base = "https://download.copr.fedorainfracloud.org/results"
    fullname = f"{owner}/{project}"
    destdir = f"{build_id:08d}-{package}"
    return f"{base}/{fullname}/{chroot}/{destdir}/fedora-review/review.txt"


def rhbz_number(projectname):
    """
    We should instead have a database mapping BUILD_ID to RHBZ_ID
    but that's too much work for a prototype
    """
    split = projectname.split("-", 3)
    if len(split) < 4:
        return None
    if split[0] != "fedora" and split[1] != "review":
        return None
    if not split[2].isnumeric():
        return None
    return split[2]


def render_bugzilla_comment(build_url, build_status,
                            review_template_url, issues):
    loader = jinja2.FileSystemLoader(".")
    env = jinja2.Environment(loader=loader)
    template = env.get_template("bugzilla-comment.j2")
    values = {
        "build_url": build_url,
        "build_status": build_status,
        "review_template_url": review_template_url,
        "issues": issues,
    }
    return template.render(**values)


def submit_bugzilla_comment(text):
    print(text)
    print("\n-------------------------------\n")


def save_message(message):
    with open("/home/jkadlcik/messages.log", "a") as f:
        f.write(str(message))


if __name__ == "__main__":
    conf.setup_logging()
    consume(consume)
