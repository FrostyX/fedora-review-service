#!/usr/bin/python3

from copr.v3 import CoprRequestException
from fedora_messaging.api import consume
from fedora_messaging.config import conf
from fedora_review_service.config import config
from fedora_review_service.helpers import (
    get_log,
    find_srpm_url,
    find_fas_username,
    remote_spec,
)
from fedora_review_service.logic.copr import (
    submit_to_copr,
    copr_review_spec_diff,
    copr_last_two_builds,
    copr_build_url,
)
from fedora_review_service.logic.rhbz import (
    get_bug,
    bugzilla_attach_file,
    bugzilla_submit_comment,
)
from fedora_review_service.logic.pagure import (
    pagure_client,
    query_distgit_user,
    request_for_user_exists,
    is_packager,
    is_sponsor,
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
from fedora_review_service.templates import (
    BugzillaComment,
    SponsorRequestIssue,
    SponsorRequestComment,
    SponsorRequestBugzilla,
)
from fedora_review_service.messages.copr import Copr
from fedora_review_service.messages.bugzilla import (
    Bugzilla,
    recognize,
    CommentWithSRPM,
    ManualTrigger,
    FedoraReviewPlus,
)


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

    bug = get_bug(copr.rhbz_number)

    # Sometimes people are fast and give fedora-review+ before the Copr build
    # even finishes. In such cases, we don't want to post any comments anymore
    # they would only confuse the contributor
    if not is_rhbz_ticket_open(bug):
        log.info("Not commenting on #%s, it is already closed "
                 "or has fedora-review+", bug.id)
        return

    try:
        upload_bugzilla_patch(copr.rhbz_number, copr.ownername, copr.projectname)
        log.info("RHBZ: #%s, patch uploaded", bug.id)

        spec = remote_spec(copr.spec_url)
        url = None
        if not bug.url and spec and spec.url:
            url = spec.url

        log.info("RHBZ: #%s, URL: %s", bug.id, url)
        comment = BugzillaComment(copr).render()
        log.info("RHBZ: #%s, Comment: %s", bug.id, comment)
        submit_bugzilla_comment(copr.rhbz_number, comment, url)
        log.info("RHBZ: #%s, comment submitted", bug.id)
    except Exception as ex:
        log.error("FAILED TO COMMENT ON RHBZ: #%s", bug.id)
        log.exception(ex)

    msgobj.done = True
    session.commit()
    log.info("Finished processing Copr message: %s", message.id)


def handle_bugzilla_message(message):
    bz = recognize(message)
    if not bz:
        log.info("Unrecognized Bugzilla message: %s", message.id)
        return

    name = bz.__class__.__name__
    log.info("Recognized %s message: %s", name, message.id)

    if isinstance(bz, CommentWithSRPM):
        handle_build(message, bz, bz.srpm_url)

    elif isinstance(bz, ManualTrigger):
        srpm_url = get_latest_srpm_url(bz.id, bz.packagename)
        handle_build(message, bz, srpm_url)

    elif isinstance(bz, FedoraReviewPlus):
        handle_review_plus(bz)

    log.info("Finished processing %s message: %s", name, message.id)


def handle_build(message, bz, srpm_url):
    msgobj = new_message(message)
    ticket = new_ticket(bz.id, bz.owner)
    session.commit()

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


def handle_review_plus(bz):
    bug = get_bug(bz.id)

    fas = find_fas_username(bug.comment)
    if not fas:
        log.error("Unable to parse FAS username for: %s", bug.weburl)
        return

    user = query_distgit_user(fas)
    if not user:
        log.error("Unable to query user from DistGit: %s", fas)
        return

    # It's hard to test in real life since I am already a packager. Making my
    # life easier by allowing the packager check to be skipped.
    if not config["sponsors"]["skip_packager_check"] and is_packager(fas):
        log.info("Contributor %s is already a packager", fas)
        return

    # TODO We need to check if fedora-review+ was given by a sponsor.
    # The problem is, we probably don't have any way to convert our Bugzilla
    # reviewer account to their FAS username
    if is_sponsor(None):
        log.info("The package was reviewed by a sponsor. Ticket not needed.")
        return

    pagure = pagure_client(config)
    sponsorship_request = request_for_user_exists(pagure, fas)
    if sponsorship_request:
        log.info("Sponsorship request for %s already exists: %s",
                 fas, sponsorship_request["full_url"])
        return

    # Now it's probably a good idea to create the ticket
    title = "Requesting sponsorship for {0}".format(fas)
    log.info(title)

    # Message for other sponsors
    content = SponsorRequestIssue(bz, fas).render()
    issue = pagure.create_issue(title, content)
    url = issue["issue"]["full_url"]
    log.info("Created issue: %s", url)

    # Comment for the contributor
    content = SponsorRequestComment(bz, fas).render()
    comment = pagure.comment_issue(issue["issue"]["id"], content)
    log.info("Commented on issue: %s", url)

    # Bugzilla comment for the contributor
    content = SponsorRequestBugzilla(bz, fas, url).render()
    submit_bugzilla_comment(bug.id, content)
    log.info("Commented in Bugzilla: %s", bug.weburl)


def get_latest_srpm_url(bug_id, packagename):
    bug = get_bug(bug_id)
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

    log.info("Patch for RHBZ #%s", bug_id)
    log.info("New patch: %s", filename)
    log.info("Patch description: %s", description)
    log.info(diff)
    log.info("\n-------------------------------\n")
    if not config["bugzilla_readonly"]:
        bugzilla_attach_file(bug_id, filename, diff, description)
    log.info("Patch uploaded successfully")


def submit_bugzilla_comment(bug_id, text, url=None):
    log.info("Comment for RHBZ #%s", bug_id)
    log.info("URL: %s", url or "unchanged")
    log.info(text)
    log.info("\n-------------------------------\n")
    if not config["bugzilla_readonly"]:
        bugzilla_submit_comment(bug_id, text, url)
    log.info("Comment submitted successfully")


def is_rhbz_ticket_open(bug):
    # Just so we don't have to mock this all the time in tests
    if config["bugzilla_readonly"]:
        return True

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
