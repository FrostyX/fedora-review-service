# fedora-review-service

Fedora package reviews CI


## Motivation

For years, there has been a queue of
[hundreds of packages](https://fedoraproject.org/PackageReviewStatus/reviewable.html)
waiting to be reviewed and added to Fedora. Clearly, we don't have
enough manpower to process the queue.

This project aims to provide a CI for automatically building and
reviewing the packages, and helping contributors with fixing the
most obvious issues. Therefore reducing the time that a reviewer needs
to spend on each package as much as possible.


## Goals

- Listen `fedora-messaging` messages about new RHBZ package review
  tickets, and new comments in them containing updated packages
- Create a new Copr project for each review and build the packages
- Listen `fedora-messaging` messages about finished Copr builds, and
  parse the review.json file
- Submit comments to RHBZ tickets helping both contributors and
  reviewers


## Running

### Run from git repository

```bash
PYTHONPATH=. fedora-messaging --conf conf/fedora.toml consume --callback="fedora_review_service.consumer:consume"
```


### Docker compose


You can also run the service inside a Docker container

```
docker-compose up -d
```

### OpenShift

See [more about OpenShift deployment](doc/openshift.md)


## Configuration

Doesn't matter if you are running this service on your host system, in
a `docker-compose` or in OpenShift, a manual step is required. Please
[configure your API tokens first](doc/tokens.md)

Just for the record, we are using `fedora-messaging` configuration file from
here https://github.com/fedora-infra/fedora-messaging/blob/stable/configs/


## Misc

You can see the `fedora-messaging` feed in your browser
https://apps.fedoraproject.org/datagrepper/v2/search


## Tests

```
CONFIG=conf/fedora-review-service-tests.yaml python -m pytest -vv -s
```
