FROM gitpod/workspace-postgres

ARG PYTHON_VERSION=3.10.7
RUN pyenv install "$PYTHON_VERSION" && \
    pyenv global "$PYTHON_VERSION"

RUN curl -L https://fly.io/install.sh | sh
ENV FLYCTL_INSTALL="/home/gitpod/.fly"
ENV PATH="$FLYCTL_INSTALL/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python3 -

# Override the DATABASE_URL set in gitpod/workspace-postgres
# because it does not contain the database name
# https://github.com/gitpod-io/workspace-images/blob/99de871d7ff8b7d914f34fff166398673202d63d/chunks/tool-postgresql/Dockerfile#L26
ENV DATABASE_URL=postgres://gitpod@localhost/postgres
