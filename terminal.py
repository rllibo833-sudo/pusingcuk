#!/usr/bin/env python3
"""Terminal interaktif sederhana untuk bahasa Pusingcuk."""
import sys

from evaluator import run


HELP = """Perintah terminal Pusingcuk
  Tulis program dari 'jancuk' sampai 'selesai jancuk'.
  Ketik ':contoh' untuk contoh program.
  Ketik ':batal' untuk membatalkan program yang sedang ditulis.
  Ketik ':keluar' untuk menutup terminal.
"""

EXAMPLE = """jancuk
lah angka = 3 + 4
hedeh angka
selesai jancuk"""


def main():
    print("Pusingcuk Terminal 0.1")
    print("Ketik :bantuan untuk petunjuk, :keluar untuk keluar.")
    lines = []

    while True:
        try:
            prompt = "pusingcuk> " if not lines else "......> "
            line = input(prompt)
        except (EOFError, KeyboardInterrupt):
            print("\nSampai jumpa!")
            return 0

        command = line.strip().lower()
        if not lines and command in (":keluar", ":exit", ":quit"):
            print("Sampai jumpa!")
            return 0
        if not lines and command in (":bantuan", ":help", "?"):
            print(HELP)
            continue
        if not lines and command == ":contoh":
            try:
                run(EXAMPLE)
            except (SyntaxError, RuntimeError, ValueError, TypeError, IndexError) as exc:
                print(f"Kesalahan: {exc}", file=sys.stderr)
            continue
        if not lines and command == ":batal":
            print("Tidak ada program yang sedang ditulis.")
            continue

        if lines and command == ":batal":
            lines.clear()
            print("Program dibatalkan.")
            continue

        lines.append(line)
        source = "\n".join(lines).strip()
        if source.endswith("selesai jancuk"):
            try:
                run(source)
            except (SyntaxError, RuntimeError, ValueError, TypeError, IndexError) as exc:
                print(f"Kesalahan: {exc}", file=sys.stderr)
            finally:
                lines.clear()


if __name__ == "__main__":
    raise SystemExit(main())
