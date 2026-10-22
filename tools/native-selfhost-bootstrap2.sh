#!/bin/sh
# Two-stage self-hosting check: interpreted .cuk frontend -> stage-1 bytecode
# frontend -> stage-2 bytecode frontend. No Python is used in this path.
set -eu
if [ "$#" -ne 1 ]; then
    echo "usage: $0 NATIVE_BINARY" >&2
    exit 2
fi
native=$1
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
cd "$root"
tmp=$(mktemp -d "${TMPDIR:-/tmp}/pusingcuk-bootstrap2.XXXXXX")
trap 'rm -rf "$tmp"' EXIT HUP INT TERM

# Assemble the self-hosted frontend and its driver into one valid .cuk module.
sed '$d' examples/self_hosting/compiler.cuk > "$tmp/frontend.cuk"
sed '1d;$d' examples/self_hosting/compiler_driver.cuk >> "$tmp/frontend.cuk"
printf '%s\n' 'selesai jancuk' >> "$tmp/frontend.cuk"

# Stage 0: the native runtime executes compiler.cuk to emit IR for itself.
"$native" --json-quote "$tmp/frontend.cuk" > "$tmp/source.json"
printf '{"source_name":"compiler.cuk","source":%s}\n' "$(cat "$tmp/source.json")" > "$tmp/bootstrap.payload"
tools/run_native_selfhost_frontend.sh "$native" "$tmp/bootstrap.payload" > "$tmp/stage0.ir"
if grep -q '^SELFHOST_' "$tmp/stage0.ir"; then
    cat "$tmp/stage0.ir" >&2
    exit 1
fi

# Stage 0 .cuk codegen emits the executable stage-1 compiler bytecode.
"$native" examples/self_hosting/ir_codegen.cuk < "$tmp/stage0.ir" > "$tmp/stage1.bytecode"
if grep -q '^BYTECODE_ERROR:' "$tmp/stage1.bytecode"; then
    cat "$tmp/stage1.bytecode" >&2
    exit 1
fi

# Stage 1: compiled frontend emits IR for a probe program.
printf '%s\n' '{"source_name":"probe.cuk","source":"jancuk\\nhedeh 123\\nselesai jancuk\\n"}' > "$tmp/probe.payload"
"$native" --run-bytecode "$tmp/stage1.bytecode" < "$tmp/probe.payload" > "$tmp/stage1.ir"
if grep -q '^SELFHOST_' "$tmp/stage1.ir"; then
    cat "$tmp/stage1.ir" >&2
    exit 1
fi

# Stage 1 IR codegen emits stage-2 compiler bytecode; run it on the same probe.
"$native" examples/self_hosting/ir_codegen.cuk < "$tmp/stage1.ir" > "$tmp/stage2.bytecode"
if grep -q '^BYTECODE_ERROR:' "$tmp/stage2.bytecode"; then
    cat "$tmp/stage2.bytecode" >&2
    exit 1
fi
"$native" --run-bytecode "$tmp/stage2.bytecode" < "$tmp/probe.payload" > "$tmp/stage2.ir"
if grep -q '^SELFHOST_' "$tmp/stage2.ir"; then
    cat "$tmp/stage2.ir" >&2
    exit 1
fi

# Bootstrap is valid only if both compiled generations produce identical IR.
if ! cmp -s "$tmp/stage1.ir" "$tmp/stage2.ir"; then
    echo "bootstrap gagal: IR stage-1 dan stage-2 berbeda" >&2
    diff -u "$tmp/stage1.ir" "$tmp/stage2.ir" >&2 || true
    exit 1
fi
printf '%s\n' "BOOTSTRAP2_OK: stage-1 dan stage-2 menghasilkan IR identik."
