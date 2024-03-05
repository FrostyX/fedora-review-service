# Statistics

This document describes how to generate statistics about the Fedora
Review Service usage and helpfulness. Nice for an annual humble brag.

We have multiple different scripts for printing statistics. You must
run them one by one and then manually compile the results together.

Run them from the git root.

First:

```bash
PYTHONPATH=. run/fedora-review-service-stats-bugzilla
```

Second:

```bash
PYTHONPATH=. run/fedora-review-service-stats-copr
```

Third. You probably want to download the production database to your
computer or at least back up the database first.

```bash
PYTHONPATH=. run/fedora-review-service-stats-database /path/to/the/database.sqlite
```

Also, mention how many tickets are in this category
https://fedoraproject.org/PackageReviewStatus/triaged.html
