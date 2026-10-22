#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
    echo "usage: $0 NATIVE_BINARY PAYLOAD_JSON" >&2
    exit 2
fi
native=$1
payload=$2
tmp=$(mktemp "${TMPDIR:-/tmp}/pusingcuk-selfhost.XXXXXX.cuk")
trap 'rm -f "$tmp"' EXIT HUP INT TERM
sed '$d' examples/self_hosting/compiler.cuk > "$tmp"
cat examples/self_hosting/compiler_driver.cuk >> "$tmp"
printf '%s\n' 'selesai jancuk' >> "$tmp"
"$native" "$tmp" < "$payload"
