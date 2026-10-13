# Distribusi dan Verifikasi Android

Dokumen ini memisahkan tiga hal yang tidak boleh disamakan: cross-build Android, uji eksekusi Android, dan verifikasi langsung pada perangkat Termux.

## Sumber dan ekstensi

Program Pusingcuk baru sebaiknya memakai ekstensi kanonis `.cuk`. Ekstensi `.pusingcuk` tetap didukung untuk kompatibilitas. Runtime native C menjalankan subset fitur yang dicatat di [matriks runtime](NATIVE_RUNTIME.md); binary Android tidak otomatis memiliki kemampuan yang sama dengan interpreter Python.

## Build Android NDK dari source

Di Linux dengan Android SDK dan NDK `27.2.12479018` terpasang:

```sh
export ANDROID_HOME="$HOME/Android/Sdk"
bash scripts/build-android.sh dist/android
```

Skrip menghasilkan dua executable:

- `dist/android/pusingcuk-native-android-arm64` — target Android ARM64, minimum API 24.
- `dist/android/pusingcuk-native-android-x86_64` — target Android x86-64 untuk emulator dan smoke test.

Skrip memeriksa ELF machine architecture menggunakan `readelf`, permission executable, `--version`, dan menghitung SHA-256. Compiler NDK dipatok versinya oleh workflow agar build bisa direproduksi.

## Bukti CI saat ini

Workflow [Android native runtime](../.github/workflows/android-native.yml):

1. Membuat kedua target menggunakan Android NDK.
2. Memverifikasi ELF architecture dan bit executable.
3. Menjalankan binary Android x86-64 pada Android API 35 emulator dengan program `halo.cuk`.
4. Memeriksa output program dan versi runtime.
5. Mengunggah kedua binary sebagai artifact CI selama 14 hari.

Ini membuktikan bahwa source native bisa dibangun untuk Android dan bahwa executable yang dibangun untuk ABI emulator dapat berjalan di Android. Itu **belum membuktikan** bahwa binary ARM64 sudah diuji pada perangkat fisik ARM64 yang menjalankan Termux. CI emulator x86-64 tidak bisa membuktikan kondisi runtime ARM64 pada ponsel pengguna.

## Jalur yang disarankan untuk Termux ARM64

Jalur paling dapat diandalkan di perangkat sekarang adalah membangun dengan compiler Termux sendiri:

```sh
pkg update
pkg install git clang make
git clone https://github.com/rllibo833-sudo/pusingcuk.git
cd pusingcuk
bash scripts/install-termux.sh
pusingcuk-native halo.cuk
make test-native
```

Di perangkat ARM64, sebelum mengklaim verifikasi Termux, jalankan dan catat:

```sh
uname -m
file "$PREFIX/bin/pusingcuk-native"
pusingcuk-native --version
pusingcuk-native halo.cuk
make test-native
```

Simpan model perangkat, versi Android, versi Termux, versi Clang, hasil tes, dan output yang diharapkan. Jangan mencantumkan perangkat sebagai telah teruji sebelum tes ini benar-benar dilakukan.

## Binary Release

Asset `pusingcuk` pada release `v0.7.1` adalah executable PyInstaller Linux x86-64, **bukan** executable Android. Workflow rilis yang baru akan menyertakan asset `pusingcuk-native-android-arm64` untuk rilis yang dibuat dari commit yang memuat perubahan workflow tersebut. Jangan menganggap asset Android telah tersedia pada release lama.

Binary native bukan sandbox dan harus dijalankan hanya untuk kode yang dipercaya. Binary yang dibangun dengan NDK dan yang dibangun dengan Termux berasal dari source C yang sama, tetapi toolchain dan lingkungan runtime berbeda; pertahankan tes perangkat nyata sebagai pemeriksaan terakhir.
