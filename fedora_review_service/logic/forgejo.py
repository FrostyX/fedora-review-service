import os
from ogr.services.forgejo import ForgejoService
from ogr.abstract import IssueStatus


def forgejo_packager_sponsors_project(config):
    token = read_forgejo_apikey(config["sponsors"]["forgejo_apikey_file"])
    service = ForgejoService(
        instance_url=config["sponsors"]["forgejo_instance"],
        token=token,
    )
    namespace, repo = config["sponsors"]["repo"].split("/", 1)
    return service.get_project(namespace=namespace, repo=repo)


def read_forgejo_apikey(path):
    with open(os.path.expanduser(path), "r") as fp:
        return fp.read().strip()


def request_for_user_exists(project, username):
    expected_title = "Requesting sponsorship for {0}".format(username)
    expected_content = "(FAS @{0})".format(username)

    issues = project.get_issue_list(status=IssueStatus.open)
    for issue in issues:
        if issue.title != expected_title:
            continue
        if expected_content not in issue.description:
            continue
        return issue
    return False


def forgejo_issue_web_url(issue):
    return f"{issue.project.get_web_url()}/issues/{issue.id}"
