from copr.v3 import Client, CoprRequestException
from fedora_review_service.config import config
from fedora_review_service.helpers import remote_diff


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
        raise CoprRequestException(str(ex)) from ex


def submit_to_copr(rhbz, packagename, srpm_url):
    client = Client.create_from_config_file(path=config["copr_config"])
    owner = config["copr_owner"]
    project = "fedora-review-{0}-{1}".format(rhbz, packagename)
    chroots = config["copr_chroots"]
    description=("This project contains builds from Fedora Review ticket "
                 "[RHBZ #{0}](https://bugzilla.redhat.com/show_bug.cgi?id={0})."
                 .format(rhbz))
    instructions=("Please avoid using this repository unless you are reviewing "
                  "the package.")
    create_copr_project_safe(client, owner, project, chroots,
                             description=description, instructions=instructions)

    result = client.build_proxy.create_from_url(owner, project, srpm_url)
    return result["id"]


def copr_last_two_builds(ownername, projectname):
    client = Client.create_from_config_file(path=config["copr_config"])
    pagination = {"limit": 2}
    builds = client.build_proxy.get_list(
        ownername, projectname, pagination=pagination)
    return list(reversed(builds)) if len(builds) == 2 else None


def copr_review_spec_diff(builds):
    if len(builds) < 2:
        return None

    name1 = copr_build_url(builds[0].id)
    name2 = copr_build_url(builds[1].id)

    url1 = copr_spec_url_for_build(builds[0])
    url2 = copr_spec_url_for_build(builds[1])

    return remote_diff(url1, url2, name1, name2)


def copr_build_url(build_id):
    url = "{0}/coprs/build/{1}"
    return url.format(config["copr_url"], build_id)


def copr_destdir_url(owner, project, package, chroot, build_id):
    base = "{0}/results".format(config["copr_be_url"])
    fullname = "{0}/{1}".format(owner, project)
    destdir = f"{build_id:08d}-{package}"
    return f"{base}/{fullname}/{chroot}/{destdir}"


def copr_spec_url_for_build(build):
    packagename = build.source_package["name"]
    url = copr_destdir_url(
        build["ownername"],
        build["projectname"],
        packagename,
        "fedora-rawhide-x86_64",
        build["id"]
    )
    return "{0}/{1}.spec".format(url, packagename)
