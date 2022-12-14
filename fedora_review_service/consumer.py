#!/usr/bin/python3

from copr.v3 import CoprRequestException
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.config import config
from fedora_review_service.helpers import get_log
from fedora_review_service.logic.copr import (
    submit_to_copr,
    copr_review_spec_diff,
    copr_last_two_builds,
)
from fedora_review_service.logic.rhbz import (
    bugzilla_attach_file,
    bugzilla_submit_comment,
)
from fedora_review_service.database import (
    create_db,
    Ticket,
    Build,
    Message,
    new_message,
    new_ticket,
    new_build,
    session,
)
from fedora_review_service.bugzilla_comment import BugzillaComment
from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import Bugzilla


log = get_log()
create_db()


def consume(message):
    # If complicated, switch to class
    # https://fedora-messaging.readthedocs.io/en/latest/consuming.html#the-callback
    dispatch(message)


def dispatch(message):
    if message.topic in config["copr_messages"]:
        return handle_copr_message(message)

    if message.topic in config["bugzilla_messages"]:
        return handle_bugzilla_message(message)


def handle_copr_message(message):
    copr = Copr(message)
    if copr.ignore:
        return

    log.info("Recognized Copr message: %s", message.id)
    msgobj = new_message(message)

    build = session.query(Build).filter(Build.copr_build_id==copr.build_id).first()
    if not build:
        log.info("The build #%s wasn't submitted by this "
                 "fedora-review-service instance, skipping.", copr.build_id)
        return

    build.copr_message_id = msgobj.id

    # TODO We are waiting for JSON support in fedora-review to implement these
    build.issues = None
    build.status = None

    session.commit()

    upload_bugzilla_patch(copr.rhbz_number, copr.ownername, copr.projectname)
    comment = BugzillaComment(copr).render()
    submit_bugzilla_comment(copr.rhbz_number, comment)

    msgobj.done = True
    session.commit()
    log.info("Finished processing Copr message: %s", message.id)


def handle_bugzilla_message(message):
    bz = Bugzilla(message)
    if bz.ignore:
        return

    log.info("Recognized Bugzilla message: %s", message.id)
    msgobj = new_message(message)
    ticket = new_ticket(bz.id, bz.owner)
    session.commit()

    build_id = None
    if not config["copr_readonly"]:
        try:
            log.info("Going to submit a Copr build")
            log.info("RHBZ: %s, Package: %s, SRPM: %s",
                     bz.id, bz.packagename, bz.srpm_url)
            build_id = submit_to_copr(bz.id, bz.packagename, bz.srpm_url)
            log.info("Copr build: %s", build_id)
        except CoprRequestException as ex:
            log.error("Error: {0}".format(str(ex)))

    build = new_build(ticket, bz.spec_url, bz.srpm_url, build_id, msgobj.id)

    msgobj.done = True
    session.commit()
    log.info("Finished processing Bugzilla message: %s", message.id)


def upload_bugzilla_patch(bug_id, ownername, projectname):
    builds = copr_last_two_builds(ownername, projectname)
    if not builds:
        log.info("First build for this project, nothing to diff")
        return

    diff = copr_review_spec_diff(builds)
    if not diff:
        log.info("This build's spec file and the previous spec are the same")
        return

    filename = "spec-from-{0}-to-{1}.diff".format(builds[0].id, builds[1].id)
    description = ("The .spec file difference from Copr build {0} to {1}"
                   .format(builds[0].id, builds[1].id))

    log.info("RHBZ #%s", bug_id)
    log.info("New patch: %s", filename)
    log.info("Patch description: %s", description)
    log.info(diff)
    log.info("\n-------------------------------\n")
    if not config["bugzilla_readonly"]:
        bugzilla_attach_file(bug_id, filename, diff, description)


def submit_bugzilla_comment(bug_id, text):
    log.info("RHBZ #%s", bug_id)
    log.info(text)
    log.info("\n-------------------------------\n")
    if not config["bugzilla_readonly"]:
        bugzilla_submit_comment(bug_id, text)


if __name__ == "__main__":
    create_db()
    conf.setup_logging()
    consume(consume)
