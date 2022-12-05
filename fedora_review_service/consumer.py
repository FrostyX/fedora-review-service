#!/usr/bin/python3

from copr.v3 import CoprRequestException
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.helpers import submit_to_copr
from fedora_review_service.bugzilla_comment import BugzillaComment
from fedora_review_service.database import create_db, save_message, mark_done
from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import Bugzilla


conf.setup_logging()


def consume(message):
    # If complicated, switch to class
    # https://fedora-messaging.readthedocs.io/en/latest/consuming.html#the-callback
    create_db()
    dispatch(message)


def dispatch(message):
    # FIXME It seems that this is called after every chroot ends
    if message.topic == "org.fedoraproject.prod.copr.build.end":
        return handle_copr_message(message)

    # Even newly created bugs has org.fedoraproject.prod.bugzilla.bug.update
    if message.topic == "org.fedoraproject.prod.bugzilla.bug.update":
        return handle_bugzilla_message(message)


def handle_copr_message(message):
    copr = Copr(message)
    if copr.ignore:
        return
    save_message(message)

    comment = BugzillaComment(copr).render()
    submit_bugzilla_comment(comment)
    mark_done(message)


def handle_bugzilla_message(message):
    bz = Bugzilla(message)
    if bz.ignore:
        return
    save_message(message)

    try:
        submit_to_copr(bz.id, bz.packagename, bz.srpm_url)
        mark_done(message)
    except CoprRequestException as ex:
        print("Error: {0}".format(str(ex)))


def submit_bugzilla_comment(text):
    text += "\n-------------------------------\n"
    print(text)


if __name__ == "__main__":
    create_db()
    conf.setup_logging()
    consume(consume)
