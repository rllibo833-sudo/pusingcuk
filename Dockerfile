ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential clang make git ca-certificates nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . .

# The image contains the complete build environment. Commands remain explicit
# so callers can run Python, the native compiler, bootstrap, or the full suite.
CMD ["make", "test"]
