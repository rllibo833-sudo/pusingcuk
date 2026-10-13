# Pusingcuk on Termux

This guide is for running Pusingcuk on an Android phone using Termux. It does **not** require Android Studio or building an APK.

## Option 1: Run the Python reference interpreter

Install Termux packages, get the source, then run the bundled example:

```sh
pkg update
pkg install python git
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
python pusingcuk_new.py halo.cuk
```

To check syntax without executing the program:

```sh
python pusingcuk_new.py --check halo.cuk
```

This path follows the reference language behavior and needs Python. Use `.cuk` for new source files; old `.pusingcuk` examples remain supported.

## Option 2: Build the native C executable

The native runtime can run without Python after it has been compiled. Install the native build tools and run the repository's installer:

```sh
pkg update
pkg install git clang make
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
bash scripts/install-termux.sh
pusingcuk-native examples/native/rekap_anggaran.pusingcuk
```

The C runtime supports a smaller subset than the Python interpreter. In particular, the native module system is not available. Check the [native runtime feature list](../NATIVE_RUNTIME.md) before porting a program. If a feature is marked as reference-only or unsupported, do not assume the C executable will run it.

## Choosing a downloaded release

Do not run an asset named `pusingcuk` in Termux just because it appears under GitHub Releases. That name refers to the Linux x86-64 PyInstaller CLI in the existing release line. For Termux, build from source with the instructions above or choose a release asset explicitly named for Android ARM64 when that asset exists.

A successful NDK cross-build or Android emulator test is not the same as testing a real ARM64 Termux device. Physical device validation remains a separate step.

## Troubleshooting

- **`python: command not found`:** install Python with `pkg install python`.
- **`clang: command not found` or `make: command not found`:** install the native build tools before running the installer.
- **A program works in Python but not in C:** compare its features with the [native runtime matrix](../NATIVE_RUNTIME.md). This is a support-scope difference, not proof that source extension is wrong.
- **A syntax error:** run `python pusingcuk_new.py --check program.cuk`, then compare the statement with [the language specification](../../SPEC.md).

## More detail

- [Native Termux setup](../NATIVE_TERMUX.md)
- [Compatibility matrix](../COMPATIBILITY.md)
- [Security limits](../../SECURITY.md)

Do not execute programs from unknown sources with access to files, credentials, or sensitive data. Pusingcuk is not a sandbox.


## Menjalankan skrip `.cuk` langsung

Setelah CLI Python Pusingcuk terpasang dan tersedia di `PATH`, skrip dapat memakai shebang:

```cuk
#!/usr/bin/env pusingcuk
jancuk
hedeh "Halo, Termux"
selesai jancuk
```

Jadikan executable dan jalankan:

```sh
chmod +x script.cuk
./script.cuk
```

Di Linux desktop, ekstensi sumber didaftarkan lewat `pusingcuk.xml` (`text/x-pusingcuk`). Registrasi MIME bukan fasilitas shell yang dibutuhkan Termux.
