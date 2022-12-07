FROM registry.fedoraproject.org/fedora:37

RUN dnf -y update && \
    dnf -y install \
        jq \
        vim \
        pip \
        procps-ng \
        sqlite \
        fedora-messaging \
        python3-copr \
        python3-yaml \
        python3-jinja2 \
        python3-sqlalchemy \
        python3-ipdb \
        && \
    dnf clean all

# TODO A nice tool, package it for Fedora
RUN pip install yq


COPY conf /etc/fedora-review-service
RUN cat /etc/fedora-review-service/fedora-review-service.yaml \
    |yq '.copr_config="/private/.config/copr"' \
    |yq '.database_uri="sqlite:////database/fedora-review-service.sqlite"' \
    |yq '.log="/persistent/log/fedora-review-service.log"' \
    |yq -y '.' > /etc/fedora-review-service/fedora-review-service-production.yaml
