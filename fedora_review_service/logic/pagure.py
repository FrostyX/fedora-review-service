import os
import requests
from libpagure import Pagure


def pagure_client(config):
    token = read_pagure_apikey(config["sponsors"]["pagure_apikey_file"])
    return Pagure(
        instance_url=config["sponsors"]["pagure_instance"],
        repo_to=config["sponsors"]["repo"],
        pagure_token=token,
    )


def read_pagure_apikey(path):
    with open(os.path.expanduser(path), "r") as fp:
        return fp.read().strip()


def is_packager(username):
    groupname = "packager"
    instance = "https://src.fedoraproject.org"
    url = "{0}/api/0/group/{1}".format(instance, groupname)
    response = requests.get(url)
    data = response.json()
    return username in data["members"]


def is_sponsor(bugzilla_user_id):
    # This could be implemented using `fasjson` but but it would require us to
    # do `fkinit` on the server. Instead, use Packager Sponsors public API
    url = "https://docs.pagure.org/fedora-sponsors/api/sponsors.json"
    try:
        response = requests.get(url, timeout=10)
    except requests.exceptions.Timeout:
        return False

    # It would probably be better to use `response.raise_for_status()` but
    # I don't want to complicate the caller
    if not response.ok:
        return False

    try:
        data = response.json()
    except requests.exceptions.JSONDecodeError:
        return False

    return bugzilla_user_id in [x["bugzilla_user_id"] for x in data]


def request_for_user_exists(client, username):
    expected_title = "Requesting sponsorship for {0}".format(username)
    expected_content = "(FAS @{0})".format(username)

    issues = client.list_issues()
    for issue in issues:
        if issue["title"] != expected_title:
            continue
        if expected_content not in issue["content"]:
            continue
        return issue
    return False
