import re
from copr.v3 import CoprRequestException


def review_package_name(summary):
    right = summary.split("Review Request:")[-1]
    return right.split(" - ")[0].strip()


def create_copr_project_safe(client, owner, project, chroots,
                             description=None, instructions=None):
    try:
        client.project_proxy.add(
            owner,
            project,
            chroots=chroots,
            description=description,
            instructions=instructions,
            fedora_review=True,
        )
    except CoprRequestException as ex:
        if "already" in str(ex):
            return
        raise CoprRequestException from ex


def submit_to_copr(rhbz, summary, srpm_url):
    client = Client.create_from_config_file()
    name = review_package_name(summary)
    owner = "frostyx"
    project = "fedora-review-{0}-{1}".format(rhbz, name)
    chroots = [
        "fedora-35-x86_64",
        "fedora-36-x86_64",
        "fedora-37-x86_64",
        "fedora-rawhide-x86_64",
    ]
    description=("This project contains builds from Fedora Review ticket "
                 "[RHBZ #{0}](https://bugzilla.redhat.com/show_bug.cgi?id={0})."
                 .format(rhbz))
    instructions=("Please avoid using this repository unless you are reviewing "
                  "the package.")
    create_copr_project_safe(client, owner, project, chroots,
                             description=description, instructions=instructions)

    result = client.build_proxy.create_from_url(owner, project, srpm_url)
    return result["id"]


def find_srpm_url(text):
    srpm_url = None
    urls = re.findall("(?P<url>https?://[^\s]+)", text)
    for url in urls:
        filename = url.split("/")[-1]
        if name not in filename:
            continue
        if url.endswith(".src.rpm"):
            srpm_url = url
    return srpm_url
