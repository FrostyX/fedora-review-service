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
        python3-bugzilla \
        python3-yaml \
        python3-jinja2 \
        python3-sqlalchemy \
        python3-ipdb \
        && \
    dnf clean all

# TODO A nice tool, package it for Fedora
RUN pip install yq

# Copy source code
COPY fedora_review_service /src/fedora_review_service/

# Copy config file
COPY conf /etc/fedora-review-service
RUN cat /etc/fedora-review-service/fedora-review-service.yaml \
    |yq '.copr_config="/persistent/private/.config/copr"' \
    |yq '.database_uri="sqlite:////persistent/fedora-review-service.sqlite"' \
    |yq '.log="/persistent/log/fedora-review-service.log"' \
    |yq -y '.' > /etc/fedora-review-service/fedora-review-service-production.yaml

CMD [ "fedora-messaging", "--conf", "/etc/fedora-review-service/fedora.toml", \
      "consume", "--callback=fedora_review_service.consumer:consume"]
