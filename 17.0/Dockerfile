# Parts of both Odoo and OCA Docker files are being used. 
FROM python:3.11-slim-bullseye

ARG ODOO_VERSION=17.0
ARG DOCKER_ODOO_UID=9999  
ARG DOCKER_ODOO_GID=9999
ARG POSTGRES_VERSION=14
ARG TARGETARCH
ENV PIP_NO_CACHE_DIR=1
# This token will be used to clone private GitHub repos
ARG GITHUB_TOKEN=<token>

SHELL ["/bin/bash", "-xo", "pipefail", "-c"]

# Generate locale C.UTF-8 for postgres and general locale data
ENV LANG C.UTF-8

# Install dependencies as describe in Odoo documentation
# https://www.odoo.com/documentation/17.0/administration/install/install.html#setup-install-source-linux-git
# We also install  virtualenv package which will be created lated to create virtual environment and some dependencies needed for building packages

RUN apt-get update -qq && DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends curl python3-pip libldap2-dev libpq-dev libsasl2-dev \
    python3-dev python3-virtualenv build-essential gnupg npm git \
    # OCA extra deps 
    # for lxml
    libxml2-dev \
    libxslt1-dev \
    libz-dev \
    libxmlsec1-dev \
    # for pycups
    libcups2-dev \
    # some other build tools
    swig \
    libffi-dev \
    pkg-config

# Install wkhtmltopdf
RUN if [ -z "${TARGETARCH}" ]; then \
    TARGETARCH="$(dpkg --print-architecture)"; \
    fi; \
    curl -sSL https://github.com/wkhtmltopdf/packaging/releases/download/0.12.6.1-3/wkhtmltox_0.12.6.1-3.bullseye_${TARGETARCH}.deb -o /tmp/wkhtml.deb \
    && apt-get update -qq \
    && dpkg --force-depends -i /tmp/wkhtml.deb \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq -f --no-install-recommends \
    && rm /tmp/wkhtml.deb

    # Install latest version of the PG client
RUN curl -sSL https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - \
    && echo "deb http://apt.postgresql.org/pub/repos/apt/ bullseye-pgdg main" > /etc/apt/sources.list.d/pgclient.list \
    && apt-get update -qq \
    && DEBIAN_FRONTEND=noninteractive apt-get install -qq postgresql-client-${POSTGRES_VERSION}

# Install nodejs dependencies
RUN npm install -g rtlcss


# Enable VENV
ENV VIRTUAL_ENV=/opt/odoo-venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Install tools needed for custom addons installation
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir manifestoo git-aggregator click-odoo


# Install Odoo python dependencies
RUN curl https://raw.githubusercontent.com/odoo/odoo/${ODOO_VERSION}/requirements.txt > /tmp/requirements.txt && \
    pip3 install -r /tmp/requirements.txt

# Add "odoo" user. We use same guid uid as in the official Odoo image
RUN groupadd --gid ${DOCKER_ODOO_GID} odoo && useradd odoo -u ${DOCKER_ODOO_UID} -g ${DOCKER_ODOO_GID} -m -s /bin/bash

# Copy entrypoint script and Odoo configuration file
COPY ./entrypoint.sh /
COPY wait-for-psql.py /usr/local/bin/wait-for-psql.py

# Install Odoo (use ADD for correct layer caching)
# In case we need to clone specific release
ARG ODOO_HEAD=${ODOO_VERSION}
ARG ODOO_ORG_REPO=odoo/odoo
RUN mkdir /tmp/getodoo \
    && (curl -sSL https://github.com/$ODOO_ORG_REPO/tarball/$ODOO_HEAD | tar -C /tmp/getodoo -xz) \
    && mv /tmp/getodoo/* /opt/odoo \
    && rmdir /tmp/getodoo
RUN pip install --no-cache-dir -e /opt/odoo --config-setting=editable-mode=compat

# Create odoo config file 
RUN printf "[options]\ndata_dir = /var/lib/odoo\n" > /etc/odoo.conf && chown odoo /etc/odoo.conf

# Create directories for extra addons and filestore, set ownership to `odoo`
ENV ADDONS_LOCATION=/opt/odoo/addons
RUN mkdir -p /tmp/getaddons/addons \
    && chown odoo $ADDONS_LOCATION \
    && mkdir -p /var/lib/odoo && chown odoo /var/lib/odoo

    
# Clone extra addons
# This arg is used for cache invalidation so every layer below will be rebuilt
ARG EXTRA_ADDONS_RELEASE=put_any_value_here

# Copy addons list file
COPY ./addons.yml /tmp/getaddons

# Git settings used by GitAggregator
ENV GIT_USERNAME="Doge"
ENV GIT_EMAIL="doge@meme.example.com"

# Run git-aggregator
RUN git config --global user.email ${GIT_EMAIL} && git config --global user.name ${GIT_USERNAME} && \
    cd /tmp/getaddons && gitaggregate -c  /tmp/getaddons/addons.yml --expand-env

# Move all addons to their final destination
ENV ADDONS_DIR=/opt/extra-addons
RUN mkdir $ADDONS_DIR \
    && chown odoo $ADDONS_DIR \
    && cd /tmp/getaddons && find . -mindepth 2 -maxdepth 2 -type d -not \( -name '.*' -o -name 'setup' \) -exec mv -f {} $ADDONS_DIR \; \
    && ls -lah $ADDONS_DIR && rm -rf /tmp/getaddons

# Install external dependencies
RUN deps=$(manifestoo -d $ADDONS_DIR list-external-dependencies deb --transitive --ignore-missing) && \
    if [ -n "$deps" ]; then \
        apt-get update -qq && \
        DEBIAN_FRONTEND=noninteractive apt-get install -qq --no-install-recommends ${deps}; \
    fi


# Create hatch config file
RUN printf "[build-system]\nrequires = ['hatchling', 'hatch-odoo']\nbuild-backend = 'hatchling.build'\n\n[project]\nname = 'extra-addons'\nversion = '1.0'\ndynamic = ['dependencies']\n\n[tool.hatch.metadata.hooks.odoo-addons-dependencies]\n\n[tool.hatch.build.hooks.odoo-addons-dirs]\n\n[tool.hatch-odoo]\nodoo_version_override = '17.0'\ndependencies = ['click-odoo-contrib']\naddons_dirs = ['.']\n" > $ADDONS_DIR/pyproject.toml

# This PEP 503 index uses odoo addons from OCA and redirects the rest to PyPI,
# in effect hiding all non-OCA Odoo addons that are on PyPI.
ENV PIP_INDEX_URL=https://wheelhouse.odoo-community.org/oca-simple-and-pypi

# Install extra addons
RUN cd $ADDONS_DIR && pip install -e .

# Expose filestore
VOLUME ["/var/lib/odoo"]

# Expose Odoo services
EXPOSE 8069 8071 8072

# Set the default config file
ENV ODOO_RC /etc/odoo.conf

# Set db manager password
ARG DB_MANAGER_PASSWORD=suchMuchPassword
RUN grep -q '^admin_passwd =' my.cfg && sed -i "s/^admin_passwd = .*/admin_passwd = ${DB_MANAGER_PASSWORD}/" my.cfg || echo "admin_passwd = ${DB_MANAGER_PASSWORD}" >> $ODOO_RC


# Set default user when running the container
USER odoo

ENTRYPOINT ["/entrypoint.sh"]
CMD ["odoo"]