"""
Naming this rhbz.py instead of more intuitive bugzilla.py to avoid name
shadowing.

Test the code on a STG Bugzilla instance
https://bugzilla.stage.redhat.com/
"""


import io
import sys
import bugzilla
from subprocess import Popen, PIPE


BUGZILLA_URL = "https://bugzilla.redhat.com"
BUGZILLA_URL = "https://bugzilla.stage.redhat.com"


def generate_bugzillarc(token):
    cmd = " ".join([
        "yes", token, "|",
        "bugzilla", "--bugzilla", BUGZILLA_URL, "login", "--api-key",
    ])
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    proc.communicate()
    return proc


def get_bug(bug_id):
    bz = bugzilla.Bugzilla(url=BUGZILLA_URL)
    return bz.getbug(bug_id)


def bugzilla_submit_comment(bug_id, text):
    bz = bugzilla.Bugzilla(url=BUGZILLA_URL)
    update = bz.build_update(comment=text)
    return bz.update_bugs([bug_id], update)


def bugzilla_attach_file(bug_id, filename, content, description=None):
    bz = bugzilla.Bugzilla(url=BUGZILLA_URL)
    fp = io.StringIO(content)
    return bz.attachfile([bug_id], fp, description,
                         file_name=filename, is_patch=True)
