#!/bin/sh
set -eu
cd "$(dirname "$0")/../.."
docker build --pull -f tools/sandbox/Dockerfile -t pusingcuk-core-sandbox:build .
IMAGE_ID="$(docker image inspect --format '{{.Id}}' pusingcuk-core-sandbox:build)"
case "$IMAGE_ID" in
  sha256:*) IMAGE_HASH="${IMAGE_ID#sha256:}" ;;
  *) echo "Docker did not return an immutable image ID" >&2; exit 1 ;;
esac
test "${#IMAGE_HASH}" -eq 64 || { echo "Docker image ID length is invalid" >&2; exit 1; }
case "$IMAGE_HASH" in
  *[!0-9a-f]*) echo "Docker image ID contains non-hex characters" >&2; exit 1 ;;
esac
printf 'Sandbox image built. Set PUSINGCUK_SANDBOX_IMAGE=%s\n' "$IMAGE_ID"
printf 'The runner requires this exact image ID and fails closed if it is absent.\n'
