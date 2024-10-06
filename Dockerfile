FROM registry.fedoraproject.org/fedora:39

RUN dnf -y update && \
    dnf -y install \
        jq \
        vim \
        htop \
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
        python3-specfile \
        python3-libpagure \
        python3-ipdb \
        python3-flask \
        && \
    dnf clean all

# Copy source code
COPY . /src/

# Copy config file
COPY conf /etc/fedora-review-service

# Install dependencies for the Web UI that are not packaged as RPM
RUN pip install -r /src/web/requirements.txt

CMD [ "fedora-messaging", "consume", \
      "--callback=fedora_review_service.consumer:consume" ]
