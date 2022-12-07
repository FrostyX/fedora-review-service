#!/usr/bin/python3

from copr.v3 import CoprRequestException
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.helpers import get_log, submit_to_copr
from fedora_review_service.bugzilla_comment import BugzillaComment
from fedora_review_service.database import create_db, save_message, mark_done
from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import Bugzilla


log = get_log()
create_db()


def consume(message):
    # If complicated, switch to class
    # https://fedora-messaging.readthedocs.io/en/latest/consuming.html#the-callback
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

    log.info("Recognized Copr message: %s", message.id)
    save_message(message)

    comment = BugzillaComment(copr).render()
    submit_bugzilla_comment(comment)

    mark_done(message)
    log.info("Finished processing Copr message: %s", message.id)


def handle_bugzilla_message(message):
    bz = Bugzilla(message)
    if bz.ignore:
        return

    log.info("Recognized Bugzilla message: %s", message.id)
    save_message(message)

    try:
        build_id = submit_to_copr(bz.id, bz.packagename, bz.srpm_url)
        log.info("Copr build: %s", build_id)
    except CoprRequestException as ex:
        log.error("Error: {0}".format(str(ex)))

    mark_done(message)
    log.info("Finished processing Bugzilla message: %s", message.id)


def submit_bugzilla_comment(text):
    text += "\n-------------------------------\n"
    log.info(text)


if __name__ == "__main__":
    create_db()
    conf.setup_logging()
    consume(consume)
