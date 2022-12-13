import os
import re
import logging
import difflib
import requests
from fedora_review_service.config import config


def get_log():
    path = config["log"]
    os.makedirs(os.path.dirname(path), exist_ok=True)

    log = logging.getLogger("fedora-review-service")

    log.setLevel(logging.INFO)

    # Drop the default handler, we will create it ourselves
    log.handlers = []

    # Print also to stderr
    stream = logging.StreamHandler()
    stream.setFormatter(logging.Formatter("%(message)s"))
    log.addHandler(stream)

    # Add file logging
    file_log = logging.FileHandler(path)
    file_log_format = "[%(asctime)s][%(levelname)6s]: %(message)s"
    file_log.setFormatter(logging.Formatter(file_log_format))
    log.addHandler(file_log)

    return log


def review_package_name(summary):
    right = summary.split("Review Request:")[-1]
    return right.split(" - ")[0].strip()


def find_srpm_url(packagename, text):
    srpm_url = None
    urls = re.findall("(?P<url>https?://[^\s]+)", text)
    for url in urls:
        filename = url.split("/")[-1]
        if packagename not in filename:
            continue
        if url.endswith(".src.rpm"):
            srpm_url = url
    return srpm_url


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
