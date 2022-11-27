#!/usr/bin/python3

from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.helpers import submit_to_copr
from fedora_review_service.copr import Copr
from fedora_review_service.bugzilla import Bugzilla


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
    bz = Bugzilla(message)
    if bz.ignore:
        return

    # Until we farm all the test files we need
    save_message(message)
    submit_to_copr(bz.id, bz.packagename, bz.srpm_url)


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
