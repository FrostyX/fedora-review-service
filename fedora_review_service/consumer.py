#!/usr/bin/python3

from copr.v3 import CoprRequestException
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.config import config
from fedora_review_service.helpers import get_log, find_srpm_url
from fedora_review_service.logic.copr import (
    submit_to_copr,
    copr_review_spec_diff,
    copr_last_two_builds,
    copr_build_url,
)
from fedora_review_service.logic.rhbz import (
    rhbz_client,
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

    # Sometimes people are fast and give fedora-review+ before the Copr build
    # even finishes. In such cases, we don't want to post any comments anymore
    # they would only confuse the contributor
    if not is_rhbz_ticket_open(copr.rhbz_number):
        log.info("Not commenting on #%s, it is already closed "
                 "or has fedora-review+", copr.rhbz_number)
        return

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

    srpm_url = None
    if bz.is_new_srpm_build():
        srpm_url = bz.srpm_url
    elif bz.is_manual_build_trigger():
        srpm_url = get_latest_srpm_url(bz.id, bz.packagename)

    if not srpm_url:
        log.info("I don't know what to do, any SRPM URL was found, skipping.")
        return

    build_id = None
    if not config["copr_readonly"]:
        try:
            log.info("Going to submit a Copr build")
            log.info("RHBZ: %s, Package: %s, SRPM: %s",
                     bz.id, bz.packagename, srpm_url)
            build_id = submit_to_copr(bz.id, bz.packagename, srpm_url)
            log.info("Copr build: %s", copr_build_url(build_id))
        except CoprRequestException as ex:
            log.error("Error: {0}".format(str(ex)))

    build = new_build(ticket, bz.spec_url, srpm_url, build_id, msgobj.id)

    msgobj.done = True
    session.commit()
    log.info("Finished processing Bugzilla message: %s", message.id)


def get_latest_srpm_url(bug_id, packagename):
    bz = rhbz_client()
    bug = bz.getbug(bug_id)
    comments = bug.getcomments()
    for comment in reversed(comments):
        if srpm_url := find_srpm_url(packagename, comment["text"]):
            log.info("SRPM URL from Comment #%s: %s",
                     comment["count"], srpm_url)
            return srpm_url
    return None

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


def is_rhbz_ticket_open(bug_id):
    # Just so we don't have to mock this all the time in tests
    if config["bugzilla_readonly"]:
        return True

    bz = rhbz_client()
    bug = bz.getbug(bug_id)
    if bug.status == "CLOSED":
        return False

    for flag in bug.flags:
        if flag["name"] != "fedora-review":
            continue
        if flag["status"] == "+":
            return False
    return True


if __name__ == "__main__":
    create_db()
    conf.setup_logging()
    consume(consume)
