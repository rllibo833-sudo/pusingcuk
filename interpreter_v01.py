import sys
from pathlib import Path

def run(source):
    lines = source.splitlines()
    if not lines or lines[0].strip() != "jancuk":
        raise SyntaxError("Baris pertama harus 'jancuk'")

    if lines[-1].strip() != "selesai jancuk":
        raise SyntaxError("Program harus diakhiri 'selesai jancuk'")

    variables = {}

    for number, raw in enumerate(lines[1:-1], start=2):
        line = raw.strip()

        if not line or line.startswith("#"):
            continue

        if line.startswith("lah "):
            declaration = line[4:].split("=", 1)
            if len(declaration) != 2:
                raise SyntaxError(f"Baris {number}: gunakan lah nama = nilai")

            name = declaration[0].strip()
            value = declaration[1].strip()

            if not name.isidentifier():
                raise SyntaxError(f"Baris {number}: nama variabel tidak valid")

            try:
                variables[name] = eval(
                    value, {"__builtins__": {}}, variables
                )
            except Exception as exc:
                raise SyntaxError(
                    f"Baris {number}: nilai tidak valid: {exc}"
                ) from exc

        elif line.startswith("hedeh "):
            value = line[6:].strip()
            try:
                result = eval(
                    value, {"__builtins__": {}}, variables
                )
            except Exception:
                result = value.strip('"').strip("'")
            print(result)

        else:
            raise SyntaxError(
                f"Baris {number}: perintah belum didukung: {line}"
            )

def main():
    if len(sys.argv) != 2:
        print("Pemakaian: python interpreter.py program.pusingcuk")
        return

    path = Path(sys.argv[1])
    try:
        run(path.read_text(encoding="utf-8"))
    except (OSError, SyntaxError) as exc:
        print(f"pusingcuk error: {exc}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
