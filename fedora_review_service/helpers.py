import os
import re
import logging
import tempfile
import difflib
import requests
from specfile import Specfile
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
    return right.split(" - ")[0].strip()


def find_spec_url(packagename, text):
    return _find_file_url(packagename, ".spec", text)


def find_srpm_url(packagename, text):
    return _find_file_url(packagename, ".src.rpm", text)


def _find_file_url(packagename, suffix, text):
    file_url = None
    urls = re.findall("(?P<url>https?://[^\s]+)", text)
    for url in urls:
        filename = url.split("/")[-1]
        if packagename not in filename:
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
    specfile = Specfile(fp.name)
    os.remove(fp.name)
    return specfile
