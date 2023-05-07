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


def query_distgit_user(username):
    try:
        pagure = Pagure(instance_url="https://src.fedoraproject.org")
        return pagure.user_info(username)

    # Meh, libpagure really uses Exception here
    except Exception as ex:
        return None


def is_packager(username):
    groupname = "packager"
    instance = "https://src.fedoraproject.org"
    url = "{0}/api/0/group/{1}".format(instance, groupname)
    response = requests.get(url)
    data = response.json()
    return username in data["members"]


def is_sponsor(username):
    # TODO This could be easily implemented using `fasjson` but it would require
    # us to do `fkinit` on the server.
    # See https://github.com/FrostyX/fedora-sponsors/blob/main/sponsors.py
    return False


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
