ARG PYTHON_VERSION=3.12
FROM python:${PYTHON_VERSION}-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential clang make git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY . .

# All language paths (Python reference, C runtime, native frontend and .cuk
# compilation) are invoked inside this image. No host Python/C compiler needed.
ENTRYPOINT ["make"]
CMD ["test"]
