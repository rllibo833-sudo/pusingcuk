"""Portable bytecode virtual machine for PusingCuk."""
import argparse
import json
import math
import sys
import html
import csv
import io
from pathlib import Path

from compiler.bytecode import BytecodeError, validate_bytecode
from evaluator import (PusingDict, language_equal, _REPO_ROOT, _read_project_text, _write_project_text, MAX_MODULE_FILE_BYTES)
from library.builtin_contract import BUILTIN_BY_NAME


def _json_ready(value):
    if isinstance(value, PusingDict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, dict):
        return {str(key): _json_ready(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, range)):
        return [_json_ready(item) for item in value]
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise TypeError("nilai tidak dapat diserialisasi sebagai JSON")


class VMError(RuntimeError):
    pass


class VirtualMachine:
    def __init__(self, document, *, input_stream=None, output_stream=None, max_steps=100000):
        self.document = validate_bytecode(document)
        self.functions = document["functions"]
        self.input = input_stream or sys.stdin
        self.output = output_stream or sys.stdout
        self.max_steps = max_steps
        self.steps = 0

    def fail(self, line, message):
        raise VMError(f"Baris {line}: {message}")

    def tick(self, line):
        self.steps += 1
        if self.steps > self.max_steps:
            self.fail(line, "batas total instruksi tercapai")

    @staticmethod
    def pop(stack, line):
        if not stack:
            raise VMError(f"Baris {line}: stack bytecode kosong")
        return stack.pop()

    def execute(self, code, env=None, *, in_function=False, depth=0):
        if depth > 100:
            raise VMError("batas kedalaman pemanggilan fungsi tercapai")
        env = {} if env is None else env
        stack, iterators, pc = [], {}, 0
        while pc < len(code):
            op, arg, line = code[pc]
            self.tick(line)
            pc += 1
            if op == "CONST":
                stack.append(arg)
            elif op == "LOAD":
                if arg not in env: self.fail(line, f"variabel '{arg}' belum dibuat")
                stack.append(env[arg])
            elif op == "DECLARE":
                if arg in env: self.fail(line, f"variabel '{arg}' sudah dibuat")
                env[arg] = self.pop(stack, line)
            elif op == "STORE":
                if arg not in env: self.fail(line, f"variabel '{arg}' belum dibuat")
                env[arg] = self.pop(stack, line)
            elif op == "PRINT":
                value = self.pop(stack, line)
                if value is True: value = "okelah"
                elif value is False: value = "tidak"
                print(value, file=self.output)
            elif op == "INPUT":
                prompt = self.pop(stack, line)
                if not isinstance(prompt, str): self.fail(line, "prompt tanya harus berupa teks")
                if arg in env: self.fail(line, f"variabel '{arg}' sudah dibuat")
                self.output.write(prompt)
                self.output.flush()
                value = self.input.readline()
                if value.endswith("\n"): value = value[:-1]
                if value.endswith("\r"): value = value[:-1]
                env[arg] = value
            elif op == "POP":
                self.pop(stack, line)
            elif op == "MAKE_LIST":
                count = arg
                if not isinstance(count, int) or count < 0 or count > len(stack): self.fail(line, "jumlah elemen daftar tidak valid")
                values = stack[-count:] if count else []
                if count: del stack[-count:]
                stack.append(values)
            elif op == "MAKE_DICT":
                count = arg
                if not isinstance(count, int) or count < 0 or 2 * count > len(stack): self.fail(line, "jumlah entri kamus tidak valid")
                values = stack[-2 * count:] if count else []
                if count: del stack[-2 * count:]
                result = PusingDict()
                try:
                    for i in range(0, len(values), 2): result[values[i]] = values[i + 1]
                except (TypeError, ValueError) as exc:
                    self.fail(line, str(exc))
                stack.append(result)
            elif op == "GET":
                key, collection = self.pop(stack, line), self.pop(stack, line)
                if isinstance(collection, (list, str, range)):
                    if not isinstance(key, int) or isinstance(key, bool): self.fail(line, "indeks harus berupa bilangan bulat")
                    if key < 0 or key >= len(collection): self.fail(line, "indeks di luar batas")
                    stack.append(collection[key])
                elif isinstance(collection, (PusingDict, dict)):
                    try: stack.append(collection[key])
                    except (KeyError, TypeError): self.fail(line, "kunci kamus tidak ditemukan")
                else: self.fail(line, "nilai tidak dapat diindeks")
            elif op == "SET_INDEX":
                value, key, collection = self.pop(stack, line), self.pop(stack, line), self.pop(stack, line)
                if isinstance(collection, list):
                    if not isinstance(key, int) or isinstance(key, bool): self.fail(line, "indeks harus berupa bilangan bulat")
                    if key < 0 or key >= len(collection): self.fail(line, "indeks di luar batas")
                    collection[key] = value
                elif isinstance(collection, (PusingDict, dict)):
                    try: collection[key] = value
                    except (KeyError, TypeError, ValueError): self.fail(line, "kunci kamus tidak valid")
                else: self.fail(line, "assignment indeks hanya mendukung daftar dan kamus")
            elif op == "UNARY":
                value = self.pop(stack, line)
                if arg == "bukan":
                    stack.append(not value)
                elif arg == "-":
                    if isinstance(value, bool) or not isinstance(value, (int, float)):
                        self.fail(line, "operator unary '-' membutuhkan angka")
                    try:
                        result = -value
                    except (ArithmeticError, TypeError, ValueError):
                        self.fail(line, "operasi unary angka gagal")
                    if isinstance(result, float) and not math.isfinite(result):
                        self.fail(line, "operasi angka non-finite")
                    stack.append(result)
                else:
                    self.fail(line, f"operator unary tidak dikenal: {arg}")
            elif op == "BINARY":
                right, left = self.pop(stack, line), self.pop(stack, line)
                try:
                    if arg == "+" and isinstance(left, str) and isinstance(right, str):
                        result = left + right
                    elif arg == "+" and isinstance(left, list) and isinstance(right, list):
                        result = left + right
                    elif arg == "==":
                        result = language_equal(left, right)
                    elif arg == "!=":
                        result = not language_equal(left, right)
                    elif arg in ("+", "-", "*", "/", "//", "%", "<", "<=", ">", ">="):
                        # Strings support ordered comparison only against strings;
                        # booleans remain distinct from numbers in the language contract.
                        if arg in ("<", "<=", ">", ">=") and isinstance(left, str) and isinstance(right, str):
                            if arg == "<": result = left < right
                            elif arg == "<=": result = left <= right
                            elif arg == ">": result = left > right
                            else: result = left >= right
                        elif (isinstance(left, bool) or isinstance(right, bool)
                                or not isinstance(left, (int, float))
                                or not isinstance(right, (int, float))):
                            if arg == "+" and isinstance(left, str) and isinstance(right, str):
                                result = left + right
                            else:
                                self.fail(line, f"operator '{arg}' membutuhkan dua angka atau dua teks untuk perbandingan")
                        elif arg == "+":
                            result = left + right
                        elif arg == "-":
                            result = left - right
                        elif arg == "*":
                            result = left * right
                        elif arg == "/":
                            if right == 0: self.fail(line, "pembagian dengan nol")
                            result = left / right
                        elif arg == "//":
                            if right == 0: self.fail(line, "pembagian dengan nol")
                            result = left // right
                        elif arg == "%":
                            if right == 0: self.fail(line, "modulo dengan nol")
                            result = left % right
                        elif arg == "<": result = left < right
                        elif arg == "<=": result = left <= right
                        elif arg == ">": result = left > right
                        else: result = left >= right
                    else:
                        self.fail(line, f"operator tidak dikenal: {arg}")
                except VMError:
                    raise
                except Exception as exc:
                    self.fail(line, f"operasi gagal ({type(exc).__name__})")
                if isinstance(result, float) and not math.isfinite(result): self.fail(line, "operasi angka non-finite")
                stack.append(result)
            elif op == "TO_BOOL":
                stack.append(bool(self.pop(stack, line)))
            elif op in ("JUMP_IF_FALSE", "JUMP_IF_TRUE"):
                condition = bool(self.pop(stack, line))
                if (op == "JUMP_IF_FALSE" and not condition) or (op == "JUMP_IF_TRUE" and condition):
                    if not isinstance(arg, int) or arg < 0 or arg > len(code): self.fail(line, "tujuan lompatan tidak valid")
                    pc = arg
            elif op == "JUMP":
                if not isinstance(arg, int) or arg < 0 or arg > len(code): self.fail(line, "tujuan lompatan tidak valid")
                pc = arg
            elif op == "CALL":
                name, count = arg
                if not isinstance(count, int) or count < 0 or count > len(stack): self.fail(line, "jumlah argumen tidak valid")
                args = stack[-count:] if count else []
                if count: del stack[-count:]
                if name in {"jadi_json", "parse_json"}:
                    if len(args) != 1: self.fail(line, f"{name}() membutuhkan 1 argumen")
                    try: result = json.loads(args[0])
                    except (TypeError, ValueError): result = False
                elif name == "jadi_teks":
                    if len(args) != 1: self.fail(line, "jadi_teks() membutuhkan 1 argumen")
                    try: result = json.dumps(_json_ready(args[0]), ensure_ascii=False, separators=(",", ":"), allow_nan=False)
                    except (TypeError, ValueError) as exc: self.fail(line, str(exc))
                elif name in {"baca_file", "baca"}:
                    if len(args) != 1 or not isinstance(args[0], str):
                        self.fail(line, f"{name}() membutuhkan satu path berupa teks")
                    try:
                        result = _read_project_text(_REPO_ROOT, args[0], max_bytes=MAX_MODULE_FILE_BYTES)
                    except (OSError, ValueError, UnicodeError):
                        result = False
                elif name in {"tulis_file", "tulis"}:
                    if len(args) != 2 or not all(isinstance(item, str) for item in args):
                        self.fail(line, f"{name}() membutuhkan path dan teks berupa string")
                    elif len(args[1].encode("utf-8")) > MAX_MODULE_FILE_BYTES:
                        result = False
                    else:
                        try:
                            _write_project_text(_REPO_ROOT, args[0], args[1])
                            result = True
                        except (OSError, ValueError):
                            result = False
                elif name in BUILTIN_BY_NAME:
                    from library.stdlib import call_builtin
                    try:
                        result = call_builtin(name, *args)
                    except (TypeError, ValueError, OverflowError, ZeroDivisionError, NameError) as exc:
                        self.fail(line, str(exc))
                else:
                    fn = self.functions.get(name)
                    if fn is None: self.fail(line, f"fungsi '{name}' tidak dikenal")
                    if len(args) != len(fn["params"]): self.fail(line, f"fungsi '{name}' membutuhkan {len(fn['params'])} argumen")
                    local = dict(zip(fn["params"], args))
                    result = self.execute(fn["code"], local, in_function=True, depth=depth + 1)
                stack.append(result)
            elif op == "ITER_INIT":
                iterable = self.pop(stack, line)
                if not isinstance(iterable, (list, tuple, str, PusingDict, range)):
                    self.fail(line, "nilai bukan koleksi yang dapat diiterasi")
                iterators[arg] = iter(iterable)
            elif op == "ITER_NEXT":
                slot, name, target = arg
                if slot not in iterators: self.fail(line, "iterator bytecode tidak ditemukan")
                try: env[name] = next(iterators[slot])
                except StopIteration:
                    if not isinstance(target, int) or target < 0 or target > len(code): self.fail(line, "tujuan iterator tidak valid")
                    pc = target
            elif op == "RETURN":
                if not in_function: self.fail(line, "RETURN di luar fungsi")
                return self.pop(stack, line)
            else:
                self.fail(line, f"opcode tidak didukung: {op}")
        return None

    def run(self):
        return self.execute(self.document["code"])


def main(argv=None):
    parser = argparse.ArgumentParser(description="Jalankan bytecode PusingCuk portabel.")
    parser.add_argument("file", help="file bytecode JSON yang dihasilkan target vm")
    args = parser.parse_args(argv)
    try:
        with Path(args.file).open(encoding="utf-8") as stream:
            document = json.load(stream)
        VirtualMachine(document).run()
    except VMError as exc:
        print(f"Kesalahan runtime: {exc}", file=sys.stderr)
        return 1
    except (OSError, json.JSONDecodeError, BytecodeError, TypeError, ValueError) as exc:
        print(f"VM PusingCuk: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
