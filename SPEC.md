# Spesifikasi Sintaks pusingcuk v0.2-dev

## 1. Struktur program

Setiap program dimulai dengan:

    jancuk

Dan diakhiri dengan:

    selesai jancuk

## 2. Deklarasi variabel

    lah nama = "Budi"
    lah umur = 20
    lah aktif = benar

Nama variabel harus diawali huruf atau garis bawah.

Deklarasi ulang nama variabel yang sudah ada ditolak.

## 3. Assignment

    umur = umur + 1

Assignment hanya boleh dilakukan pada variabel yang sudah dibuat.

## 4. Output

    hedeh "Halo"
    hedeh umur
    hedeh umur + 1

## 5. Kondisi

    njir umur >= 18
        hedeh "Dewasa"
    kampret
        hedeh "Belum dewasa"
    selesai njir

Cabang kampret bersifat opsional.

## 6. Perulangan

    lah i = 1
    mumet i <= 3
        hedeh i
        i = i + 1
    selesai mumet

Interpreter memiliki batas 10000 iterasi per loop dan 100000 langkah eksekusi total.

## 7. Operator

Matematika: + - * / // %

Perbandingan: == != < <= > >=

Logika: dan, atau, bukan

Boolean: benar, salah

### List dan indeks

List ditulis menggunakan tanda kurung siku, misalnya `[10, 20, 30]`.
Indeks dimulai dari 0. Elemen dapat dibaca dan diubah melalui indeks.
Fungsi `panjang(list)` mengembalikan jumlah elemen.
Akses indeks di luar batas menghasilkan kesalahan.

## 8. Komentar

Baris yang setelah spasi awalnya dimulai dengan # dianggap komentar.

## 9. Penanganan kesalahan

Interpreter melaporkan kesalahan dengan nomor baris jika tersedia.

## 10. Status spesifikasi

Dokumen ini mencatat perilaku implementasi saat ini.
Fitur yang belum diuji tidak dianggap telah didukung.
