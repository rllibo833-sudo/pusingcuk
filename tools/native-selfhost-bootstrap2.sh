#!/bin/sh
# Bootstrap the .cuk-authored frontend twice using only the native C runtime.
# Stage 1 must compile the same frontend source as stage 0; stage 2 must
# produce the same probe IR as stage 1. Python is not used on this path.
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

# Assemble the frontend and JSON driver into one valid .cuk module.
sed '$d' examples/self_hosting/compiler.cuk > "$tmp/frontend.cuk"
sed '1d;$d' examples/self_hosting/compiler_driver.cuk >> "$tmp/frontend.cuk"
printf '%s\n' 'selesai jancuk' >> "$tmp/frontend.cuk"

# Stage 0: seed native runtime executes the frontend source to emit its IR.
"$native" --json-quote "$tmp/frontend.cuk" > "$tmp/source.json"
printf '{"source_name":"compiler.cuk","source":%s}\n' "$(cat "$tmp/source.json")" > "$tmp/bootstrap.payload"
tools/run_native_selfhost_frontend.sh "$native" "$tmp/bootstrap.payload" > "$tmp/stage0.compiler.ir"
if grep -q '^SELFHOST_' "$tmp/stage0.compiler.ir"; then
    cat "$tmp/stage0.compiler.ir" >&2
    exit 1
fi

# Stage 0 .cuk code generator emits executable stage-1 frontend bytecode.
"$native" examples/self_hosting/ir_codegen.cuk < "$tmp/stage0.compiler.ir" > "$tmp/stage1.bytecode"
if grep -q '^BYTECODE_ERROR:' "$tmp/stage1.bytecode"; then
    cat "$tmp/stage1.bytecode" >&2
    exit 1
fi

# Stage 1 recompiles the same frontend source. This output, not a probe,
# is the input used to build the stage-2 frontend.
"$native" --run-bytecode "$tmp/stage1.bytecode" < "$tmp/bootstrap.payload" > "$tmp/stage1.compiler.ir"
if grep -q '^SELFHOST_' "$tmp/stage1.compiler.ir"; then
    cat "$tmp/stage1.compiler.ir" >&2
    exit 1
fi
if ! cmp -s "$tmp/stage0.compiler.ir" "$tmp/stage1.compiler.ir"; then
    echo "bootstrap gagal: IR frontend stage-0 dan stage-1 berbeda" >&2
    diff -u "$tmp/stage0.compiler.ir" "$tmp/stage1.compiler.ir" >&2 || true
    exit 1
fi

# Stage 1 IR codegen builds stage-2 frontend bytecode.
"$native" examples/self_hosting/ir_codegen.cuk < "$tmp/stage1.compiler.ir" > "$tmp/stage2.bytecode"
if grep -q '^BYTECODE_ERROR:' "$tmp/stage2.bytecode"; then
    cat "$tmp/stage2.bytecode" >&2
    exit 1
fi

# Run the stage-1 and stage-2 frontends on the exact same deterministic probe.
printf '%s\n' '{"source_name":"probe.cuk","source":"jancuk\\nhedeh 123\\nselesai jancuk\\n"}' > "$tmp/probe.payload"
"$native" --run-bytecode "$tmp/stage1.bytecode" < "$tmp/probe.payload" > "$tmp/stage1.probe.ir"
if grep -q '^SELFHOST_' "$tmp/stage1.probe.ir"; then
    cat "$tmp/stage1.probe.ir" >&2
    exit 1
fi
"$native" --run-bytecode "$tmp/stage2.bytecode" < "$tmp/probe.payload" > "$tmp/stage2.probe.ir"
if grep -q '^SELFHOST_' "$tmp/stage2.probe.ir"; then
    cat "$tmp/stage2.probe.ir" >&2
    exit 1
fi

# Require identical bytes and print comparable SHA-256 evidence.
if ! cmp -s "$tmp/stage1.probe.ir" "$tmp/stage2.probe.ir"; then
    echo "bootstrap gagal: output IR probe stage-1 dan stage-2 berbeda" >&2
    diff -u "$tmp/stage1.probe.ir" "$tmp/stage2.probe.ir" >&2 || true
    exit 1
fi
if command -v sha256sum >/dev/null 2>&1; then
    hash_file() { sha256sum "$1" | awk '{print $1}'; }
elif command -v shasum >/dev/null 2>&1; then
    hash_file() { shasum -a 256 "$1" | awk '{print $1}'; }
else
    echo "bootstrap gagal: utilitas SHA-256 tidak tersedia" >&2
    exit 2
fi
stage1_hash=$(hash_file "$tmp/stage1.probe.ir")
stage2_hash=$(hash_file "$tmp/stage2.probe.ir")
printf 'BOOTSTRAP2_STAGE1_SHA256=%s\n' "$stage1_hash"
printf 'BOOTSTRAP2_STAGE2_SHA256=%s\n' "$stage2_hash"
test "$stage1_hash" = "$stage2_hash"
printf '%s\n' "BOOTSTRAP2_OK: compiler frontend stage-1 dan stage-2 menghasilkan IR identik."
