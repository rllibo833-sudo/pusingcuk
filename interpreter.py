"""Kompatibilitas interpreter lama dengan evaluator modular.

Kontrak eksekusi tunggal: sumber .cuk berbentuk teks masuk ke
Evaluator.run_module(source). Evaluator sendiri bertanggung jawab atas
parse dan eksekusi; jangan parse AST di sini lalu mengirim AST ke API teks.
"""
from evaluator import Evaluator


def run(src, filename="<input>"):
    """Jalankan sumber PusingCuk dan kembalikan environment modul.

    ``filename`` dipertahankan agar pemanggil lama tetap kompatibel. API
    evaluator saat ini belum menerima nama berkas untuk diagnostik.
    """
    evaluator = Evaluator()
    try:
        return evaluator.run_module(src)
    except RuntimeError as exc:
        # API interpreter legacy memakai SyntaxError untuk diagnostik bahasa;
        # evaluator modular memakai RuntimeError. Pertahankan batas kompatibilitas
        # di sini tanpa mengubah kontrak internal evaluator.
        raise SyntaxError(str(exc)) from exc


def main():
    import sys

    src = sys.stdin.read()
    print(run(src))


if __name__ == "__main__":
    main()
