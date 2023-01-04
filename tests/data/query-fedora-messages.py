import requests
from requests.models import PreparedRequest


def prepare_url(page=1):
    # Two days
    seconds = 172800

    # 8 hours
    seconds = 60 * 60 * 8

    url = "https://apps.fedoraproject.org/datagrepper/v2/search"
    params = {"category": "copr", "delta": seconds, "page": page}
    request = PreparedRequest()
    request.prepare_url(url, params)
    return request.url


page = 1
while True:
    url = prepare_url(page=page)
    response = requests.get(url)
    data = response.json()

    print("Page [{0}/{1}]".format(page, data["pages"]))
    if page >= data["pages"]:
        break

    for message in data["raw_messages"]:
        if message["body"]["user"] != "frostyx":
            continue

        if not message["body"]["copr"].startswith("fedora-review-"):
            continue

        print("{0}  |  {1}  |  {2}  |  {3}".format(
            message["topic"],
            message["id"],
            message["body"]["copr"],
            message["body"]["chroot"],
        ))

    page += 1
