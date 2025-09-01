FROM python:3.13-slim AS builder
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates\
 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
ENV POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1
RUN pip install --no-cache-dir "poetry==$POETRY_VERSION"
COPY pyproject.toml poetry.lock* /app/
RUN poetry install --only main --no-root
COPY ./app /app

FROM python:3.13-slim AS runtime
RUN useradd -ms /bin/bash appuser
RUN apt update && apt-get install curl -y vim
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"
RUN chmod +x kubectl
RUN mv kubectl /usr/local/bin/kubectl

COPY .kubeconfig /home/appuser/.kube/config

ARG HELM_VERSION=v3.15.2 # Specify your desired Helm version
RUN curl -fsSL https://get.helm.sh/helm-${HELM_VERSION}-linux-amd64.tar.gz | tar -xzf - -C /tmp && \
    mv /tmp/linux-amd64/helm /usr/local/bin/helm && \
    rm -rf /tmp/linux-amd64

EXPOSE 8080
USER appuser
CMD ["fastapi", "run", "--port", "8080", "form.py"]
