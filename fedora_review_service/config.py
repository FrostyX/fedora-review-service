from enum import Enum
import os
import yaml


class Keywords(Enum):
    """
    User-facing keyword enumeration
    """
    IGNORE  = '[fedora-review-service-ignore]'
    BUILD   = '[fedora-review-service-build]'


def parse_config(path=None):
    path = path or os.environ.get("CONFIG")
    if not path:
        here = os.path.dirname(os.path.abspath(__file__))
        projectdir = os.path.dirname(here)
        confdir = os.path.join(projectdir, "conf")
        path = os.path.join(confdir, "fedora-review-service.yaml")
    return yaml.safe_load(open(path))


config = parse_config()
