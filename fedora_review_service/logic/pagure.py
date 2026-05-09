import requests


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
    url = "https://packager-sponsors.fedoraproject.org/api/sponsors.json"
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
