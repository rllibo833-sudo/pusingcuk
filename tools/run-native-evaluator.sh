#!/bin/sh
set -eu
if [ "$#" -ne 1 ]; then
    echo "usage: tools/run-native-evaluator.sh NATIVE_BINARY" >&2
    exit 2
fi
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
exec "$1" examples/self_hosting/evaluator.cuk
