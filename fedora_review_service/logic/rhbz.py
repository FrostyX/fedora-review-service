"""
Naming this rhbz.py instead of more intuitive bugzilla.py to avoid name
shadowing.

Test the code on a STG Bugzilla instance
https://bugzilla.stage.redhat.com/
"""


import os
import io
import sys
import shutil
import bugzilla
from subprocess import Popen, PIPE
from fedora_review_service.config import config


def generate_bugzillarc(token):
    cmd = " ".join([
        "yes", token, "|",
        "bugzilla", "--bugzilla", config["bugzilla_url"],
        "login", "--api-key",
    ])
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    out, err = proc.communicate()
    print(out)
    if err:
        print("Err: {0}".format(err))
        return False

    split = out.decode("utf-8").strip("\n").split("API key written to")
    path = split[1].strip() if len(split) == 2 else None
    if not path:
        print("Err: Cannot parse the path")
        return False

    os.makedirs(os.path.dirname(config["bugzilla_config"]), exist_ok=True)
    shutil.move(path, config["bugzilla_config"])
    print("Created: {0}".format(config["bugzilla_config"]))
    return proc


def rhbz_client():
    return bugzilla.Bugzilla(
        url=config["bugzilla_url"],
        configpaths=[config["bugzilla_config"]],
    )


def get_bug(bug_id):
    bz = rhbz_client()
    return bz.getbug(bug_id)


def bugzilla_submit_comment(bug_id, text):
    bz = rhbz_client()
    update = bz.build_update(comment=text)
    return bz.update_bugs([bug_id], update)


def bugzilla_attach_file(bug_id, filename, content, description=None):
    bz = rhbz_client()
    fp = io.StringIO(content)
    return bz.attachfile([bug_id], fp, description,
                         file_name=filename, is_patch=True)
