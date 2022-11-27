#!/usr/bin/python3

import jinja2
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.helpers import (
    find_srpm_url,
    submit_to_copr,
    review_package_name,
)
from fedora_review_service.copr import Copr


conf.setup_logging()


def consume(message):
    # If complicated, switch to class
    # https://fedora-messaging.readthedocs.io/en/latest/consuming.html#the-callback
    dispatch(message)


def dispatch(message):
    # FIXME It seems that this is called after every chroot ends
    if message.topic == "org.fedoraproject.prod.copr.build.end":
        return handle_copr_message(message)

    if message.topic.startswith("org.fedoraproject.prod.bugzilla"):
        return handle_bugzilla_message(message)


def handle_copr_message(message):
    copr = Copr(message)
    if copr.ignore:
        return
    comment = copr.render_bugzilla_comment()
    submit_bugzilla_comment(comment)


def handle_bugzilla_message(message):
    bug = message.body["bug"]
    comment = message.body.get("comment")

    if not bug["component"] == "Package Review":
        return

    # Assignee update, CC update, flags update, etc
    if not comment:
        return

    if bug["reporter"]["login"] != comment["author"]:
        return

    # TODO If not already closed
    # {'id': 1, 'name': 'NEW'}
    bug["status"]

    # TODO If not already fedora-review+
    bug["flags"]

    packagename = review_package_name(bug["summary"])
    srpm_url = find_srpm_url(packagename, comment["body"])
    if not srpm_url:
        return

    # Until we farm all the test files we need
    save_message(message)
    submit_to_copr(bug["id"], packagename, srpm_url)


def submit_bugzilla_comment(text):
    text += "\n-------------------------------\n"
    print(text)
    save_comment(text)


def save_message(message):
    with open("/home/jkadlcik/messages.log", "a") as f:
        f.write(str(message))


def save_comment(comment):
    with open("/home/jkadlcik/comments.log", "a") as f:
        f.write(str(comment))


if __name__ == "__main__":
    conf.setup_logging()
    consume(consume)
