#!/bin/sh
set -eu
case "${PROGRAM_ID:-}" in
  budget.threshold.v1)
    binary=/opt/threshold-native
    rule=/opt/rules/threshold.cuk
    ;;
  budget.sufficiency.v1)
    binary=/opt/sufficiency-native
    rule=/opt/rules/sufficiency.cuk
    ;;
  *)
    echo "UNKNOWN_PROGRAM" >&2
    exit 64
    ;;
esac
IFS= read -r nominal || exit 64
IFS= read -r batas || exit 64
case "$nominal:$batas" in
  *[!0-9:-]*|:*|*:) echo "INVALID_INPUT" >&2; exit 65 ;;
esac
printf '%s\n%s\n' "$nominal" "$batas" | "$binary" "$rule"
