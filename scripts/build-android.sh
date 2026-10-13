#!/usr/bin/env bash
# Reproducible Android NDK cross-builds for the Pusingcuk native runtime.
# Usage: ANDROID_HOME=... bash scripts/build-android.sh [output-directory]
set -euo pipefail

ANDROID_NDK_VERSION="${ANDROID_NDK_VERSION:-27.2.12479018}"
ANDROID_API="${ANDROID_API:-24}"
ANDROID_HOME="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-}}"
OUTPUT_DIR="${1:-dist/android}"

if [[ -z "$ANDROID_HOME" ]]; then
  echo "ANDROID_HOME or ANDROID_SDK_ROOT must point to an installed Android SDK." >&2
  exit 2
fi

NDK_BIN="$ANDROID_HOME/ndk/$ANDROID_NDK_VERSION/toolchains/llvm/prebuilt/linux-x86_64/bin"
if [[ ! -x "$NDK_BIN/aarch64-linux-android${ANDROID_API}-clang" ]]; then
  echo "Android NDK compiler not found: $NDK_BIN/aarch64-linux-android${ANDROID_API}-clang" >&2
  echo "Install it with: sdkmanager \"ndk;$ANDROID_NDK_VERSION\"" >&2
  exit 2
fi

mkdir -p "$OUTPUT_DIR"
CFLAGS=(-std=c11 -O2 -Wall -Wextra -Werror)

"$NDK_BIN/aarch64-linux-android${ANDROID_API}-clang" "${CFLAGS[@]}" \
  -DPUSINGCUK_VERSION='"0.7.1-android"' \
  native/pusingcuk.c -lm -o "$OUTPUT_DIR/pusingcuk-native-android-arm64"

"$NDK_BIN/x86_64-linux-android${ANDROID_API}-clang" "${CFLAGS[@]}" \
  -DPUSINGCUK_VERSION='"0.7.1-android"' \
  native/pusingcuk.c -lm -o "$OUTPUT_DIR/pusingcuk-native-android-x86_64"

chmod 755 "$OUTPUT_DIR/pusingcuk-native-android-arm64" "$OUTPUT_DIR/pusingcuk-native-android-x86_64"

command -v file >/dev/null 2>&1 && file "$OUTPUT_DIR"/pusingcuk-native-android-*
readelf -h "$OUTPUT_DIR/pusingcuk-native-android-arm64" | grep -q "Machine:.*AArch64"
readelf -h "$OUTPUT_DIR/pusingcuk-native-android-x86_64" | grep -Eq "Machine:.*(Advanced Micro Devices X86-64|X86-64)"
strings "$OUTPUT_DIR/pusingcuk-native-android-arm64" | grep -Fq "0.7.1-android"
strings "$OUTPUT_DIR/pusingcuk-native-android-x86_64" | grep -Fq "0.7.1-android"
sha256sum "$OUTPUT_DIR"/pusingcuk-native-android-*
