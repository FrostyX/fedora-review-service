import os
import re
import logging
import tempfile
import difflib
import requests
from requests.adapters import HTTPAdapter
from specfile import Specfile
from specfile.exceptions import RPMException
from munch import Munch
from fedora_review_service.config import config


def get_log():
    log = logging.getLogger("fedora-review-service")

    log.setLevel(logging.INFO)

    # Drop the default handler, we will create it ourselves
    log.handlers = []

    # Print also to stderr
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(stream)

    # Add file logging
    path = config["log"]
    if path:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        file_log = logging.FileHandler(path)
        file_log_format = "[%(asctime)s][%(levelname)6s]: %(message)s"
        file_log.setFormatter(logging.Formatter(file_log_format))
        log.addHandler(file_log)

    return log


def review_package_name(summary):
    right = summary.split("Review Request:")[-1]
    return right.split(" - ")[0].strip().lower()


def is_valid_summary(summary):
    # This duplicates some code from `review_package_name` and it would be
    # better `review_package_name` raised exceptions if the summary isn't valid.
    # But that would require some tweaking of our error handling which is a bit
    # tricky and not covered by tests well-enough. Doing this instead to avoid
    # breakage as much as possible.
    if not "Review Request:" in summary:
        return None
    right = summary.split("Review Request:")[-1]
    return " - " in right


def find_spec_url(packagename, text):
    return _find_file_url(packagename, ".spec", text)


def find_srpm_url(packagename, text):
    return _find_file_url(packagename, ".src.rpm", text)


def find_fas_username(text):
    result = re.search(r"Fedora Account System Username:(\s*)(?P<fas>\w+)", text)
    return result.group("fas") if result else None


def fas_url(username):
    return "https://src.fedoraproject.org/user/{0}".format(username)


def _find_file_url(packagename, suffix, text):
    file_url = None
    urls = re.findall(r"(?P<url>https?://[^\s]+)", text)
    for url in urls:
        filename = url.split("/")[-1]
        if packagename.lower() not in filename.lower():
            continue
        if url.endswith(suffix):
            file_url = url
    return file_url


def remote_diff(url1, url2, name1=None, name2=None):
    response1 = requests.get(url1)
    response2 = requests.get(url2)

    if response1.status_code != 200:
        return None
    if response2.status_code != 200:
        return None

    return diff(response1.text, response2.text, name1, name2)


def diff(text1, text2, name1=None, name2=None):
    s1 = [x + "\n" for x in text1.split("\n")]
    s2 = [x + "\n" for x in text2.split("\n")]
    name1 = name1 or ""
    name2 = name2 or ""
    result = difflib.unified_diff(s1, s2, name1, name2)
    return "".join(result)


def remote_spec(url):
    """
    Return an instance of
    https://github.com/packit/specfile
    """
    response = requests.get(url)
    if response.status_code != 200:
        return None

    # https://github.com/packit/specfile/issues/206
    # from io import StringIO
    # fp = StringIO()
    # with tempfile.NamedTemporaryFile(suffix=".spec", mode="w") as fp:

    with tempfile.NamedTemporaryFile(suffix=".spec", mode="w", delete=False) as fp:
        fp.write(response.text)

    try:
        specfile = Specfile(fp.name)
    except RPMException:
        return None

    os.remove(fp.name)
    return specfile


def remote_report(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return response.json()


def is_raw_url(url):
    return "text/plain" in response.headers["content-type"]


def check_available(url):
    """
    Check if an URL (e.g. a remote SRPM file) is available without downloading
    it. In case of failure, try multiple times to be fair. Return the response
    instead of a boolean so that the caller can format a detailed explanation.
    """
    session = requests.Session()
    session.mount(url, HTTPAdapter(max_retries=5))
    try:
        response = session.head(url, timeout=30)
    except (requests.ConnectTimeout, requests.ConnectionError) as ex:
        # The timeout happens during the TCP handshake, before the response
        # object is even created. In such HTTP status code doesn't exist.
        response = Munch(ok=False, status_code=None, url=url, reason=str(ex))
    return response
