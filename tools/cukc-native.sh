#!/bin/sh
set -eu
if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
    echo "usage: tools/cukc-native.sh NATIVE_BINARY SOURCE.cuk [PROGRAM_INPUT]" >&2
    exit 2
fi
native=$1
source=$2
program_input=${3-}
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
tmp_base=${TMPDIR:-${PREFIX:+$PREFIX/tmp}}
tmp_base=${tmp_base:-/tmp}
mkdir -p "$tmp_base"
tmp=$(mktemp "$tmp_base/pusingcuk-native-compile.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
"$native" --json-quote "$source" > "$tmp/source.json"
printf '{"source_name":"input.cuk","source":%s}\n' "$(cat "$tmp/source.json")" > "$tmp/payload.json"
tools/run_native_selfhost_frontend.sh "$native" "$tmp/payload.json" > "$tmp/ir.json"
if grep -q '^SELFHOST_' "$tmp/ir.json"; then
    cat "$tmp/ir.json" >&2
    exit 2
fi
"$native" examples/self_hosting/ir_codegen.cuk < "$tmp/ir.json" > "$tmp/bytecode.json"
if grep -q '^BYTECODE_ERROR:' "$tmp/bytecode.json"; then
    cat "$tmp/bytecode.json" >&2
    exit 2
fi
if [ -n "$program_input" ]; then
    "$native" --run-bytecode "$tmp/bytecode.json" < "$program_input"
else
    "$native" --run-bytecode "$tmp/bytecode.json"
fi
