import requests
from requests.models import PreparedRequest


def prepare_url(page=1):
    url = "https://apps.fedoraproject.org/datagrepper/v2/search"

    # Bugzilla
    params = {"category": "bugzilla", "page": page,
              "start": "2023-02-23", "end": "2023-02-25"}

    # Copr
    # seconds = 7200  # Two hours
    # params = {"topic": "org.fedoraproject.prod.copr.build.end",
    #           "delta": seconds, "page": page}

    request = PreparedRequest()
    request.prepare_url(url, params)
    return request.url


def print_copr_message(message):
    if message["body"]["user"] != "frostyx":
        return
    if not message["body"]["copr"].startswith("fedora-review-"):
        return

    print_message(message, message["body"]["copr"], message["body"]["chroot"])


def print_bugzilla_message(message):
    if not message["topic"].endswith(".update"):
        return

    summary = message["body"]["bug"]["summary"]
    if not summary.startswith("Review Request:"):
        return

    if message["body"]["event"]["routing_key"] != "comment.create":
        return

    name = message["body"]["event"]["user"]["real_name"]
    print_message(message, name, summary)


def print_message(message, col3, col4):
    print("{0}  |  {1}  |  {2}  |  {3} | {4}"
          .format(message["topic"], message["id"],
                  message["headers"]["sent-at"], col3, col4))



page = 1
while True:
    url = prepare_url(page=page)
    response = requests.get(url)
    data = response.json()

    print("Page [{0}/{1}]".format(page, data["pages"]))
    if page >= data["pages"]:
        break

    for message in data["raw_messages"]:
        if message["topic"].endswith("copr.build.end"):
            print_copr_message(message)

        if message["topic"].endswith("bugzilla.bug.update"):
            print_bugzilla_message(message)

    page += 1
