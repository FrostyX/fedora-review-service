# Tokens configuration

Doesn't matter if you are running this service on your host system, in
a `docker-compose` or in OpenShift. You need to manually setup some
auth tokens.


## Copr

- Production: https://copr.fedorainfracloud.org
- Staging: https://copr.stg.fedoraproject.org

Open a Copr instance, click the API link in the footer and copy your
API token and store it to one of these locations (see the
fedora-review-service config):

- For your host system: `~/.config/copr`
- In docker: `/persistent/private/.config/copr`


## Bugzilla

- Production: https://bugzilla.redhat.com
- Staging: https://bugzilla.stage.redhat.com


Click your name in the top-right, then Preferences, API keys, and
Generate a new API key. Then you can manually store to one of these
locations (see the fedora-review-service config):

- For your host system: `~/.config/python-bugzilla/bugzillarc`
- In docker: `/persistent/private/.bugzillarc`

Or you can use the following helper:


```python
token = "L6NB04ZsFKKQaH824uqNjV5zyEUCBi8kYAVPIdUK"
from fedora_review_service.logic.rhbz import generate_bugzillarc
generate_bugzillarc(token)
```
