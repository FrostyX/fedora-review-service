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
        python-bugzilla-cli \
        python3-yaml \
        python3-jinja2 \
        python3-sqlalchemy \
        python3-alembic \
        python3-ipdb \
        && \
    dnf clean all

# Copy source code
COPY . /src/

# Copy config file
COPY conf /etc/fedora-review-service

CMD [ "fedora-messaging", "consume", \
      "--callback=fedora_review_service.consumer:consume" ]
