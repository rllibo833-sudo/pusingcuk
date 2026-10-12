"""Explicit, offline-first source-module expansion for Pusingcuk compiler targets.

Syntax:
    pakai "lib/angka.pusingcuk" sebagai angka
    ekspor fungsi tambah

Imports are static, project-root confined, and never fetched from the network.
This source expander is not a sandbox.
"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

MAX_MODULES = 128
MAX_DEPTH = 32
MAX_SOURCE_BYTES = 1_048_576
_IMPORT = re.compile(r'^\s*pakai\s+"([^"]+)"\s+sebagai\s+([A-Za-z_][A-Za-z0-9_]*)\s*$')
_EXPORT = re.compile(r'^\s*ekspor\s+fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*$')
_FUNCTION = re.compile(r'^\s*fungsi\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(')
_START = {"jancuk", "inthiseco"}
_END = {"selesai jancuk", "gitu inthiseco"}


class ModuleImportError(ValueError):
    """A deterministic module-resolution or module-contract error."""


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def _body(source: str, path: Path) -> list[str]:
    lines = source.splitlines()
    meaningful = [i for i, line in enumerate(lines) if line.strip()]
    if not meaningful:
        raise ModuleImportError(f"modul kosong: {path.name}")
    first, last = meaningful[0], meaningful[-1]
    if lines[first].strip() not in _START or lines[last].strip() not in _END:
        raise ModuleImportError(
            f"{path.name}: modul harus dibungkus jancuk ... selesai jancuk"
        )
    return lines[first + 1:last]


def _rewrite(source: str, own_names: dict[str, str],
             aliases: dict[str, dict[str, str]], path: Path) -> str:
    """Rewrite identifiers outside strings/comments; preserve original formatting."""
    out = []
    i = 0
    quote = None
    escaped = False
    while i < len(source):
        ch = source[i]
        if quote:
            out.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = None
            i += 1
            continue
        if ch in ('"', "'"):
            quote = ch
            out.append(ch)
            i += 1
            continue
        if ch == "#":
            end = source.find("\n", i)
            if end < 0:
                out.append(source[i:])
                break
            out.append(source[i:end + 1])
            i = end + 1
            continue
        if ch.isalpha() or ch == "_":
            end = i + 1
            while end < len(source) and (source[end].isalnum() or source[end] == "_"):
                end += 1
            name = source[i:end]
            if end < len(source) and source[end] == ".":
                member_start = end + 1
                member_end = member_start
                if member_start < len(source) and (
                    source[member_start].isalpha() or source[member_start] == "_"
                ):
                    member_end += 1
                    while member_end < len(source) and (
                        source[member_end].isalnum() or source[member_end] == "_"
                    ):
                        member_end += 1
                    member = source[member_start:member_end]
                    if name in aliases:
                        target = aliases[name].get(member)
                        if target is None:
                            raise ModuleImportError(
                                f"{path.name}: '{name}.{member}' bukan ekspor modul"
                            )
                        out.append(target)
                        i = member_end
                        continue
            out.append(own_names.get(name, name))
            i = end
            continue
        out.append(ch)
        i += 1
    return "".join(out)


def expand_file(source_path: str | Path, *, max_modules: int = MAX_MODULES,
                max_depth: int = MAX_DEPTH,
                max_source_bytes: int = MAX_SOURCE_BYTES) -> str:
    """Expand a .pusingcuk entry file and imports without network access."""
    entry = Path(source_path).resolve()
    root = entry.parent.resolve()
    if entry.suffix != ".pusingcuk":
        raise ModuleImportError("berkas sumber harus berekstensi .pusingcuk")
    if not entry.is_file():
        raise ModuleImportError(f"berkas sumber tidak ditemukan: {entry.name}")
    if max_modules < 1 or max_depth < 0 or max_source_bytes < 1:
        raise ModuleImportError("batas resolver harus bernilai positif")

    # Each module's source is emitted once in deterministic dependency-first order.
    cache: dict[Path, tuple[list[tuple[Path, str]], dict[str, str]]] = {}
    active: list[Path] = []
    total_bytes = 0

    def read_source(path: Path) -> str:
        nonlocal total_bytes
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ModuleImportError(f"tidak bisa membaca modul {path.name}: {exc}") from exc
        total_bytes += len(raw)
        if total_bytes > max_source_bytes:
            raise ModuleImportError("total ukuran sumber modul melewati batas")
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError as exc:
            raise ModuleImportError(f"modul bukan UTF-8: {path.name}") from exc

    def load(path: Path, depth: int) -> tuple[list[tuple[Path, str]], dict[str, str]]:
        path = path.resolve()
        if not _inside(path, root):
            raise ModuleImportError(f"impor keluar dari root proyek ditolak: {path.name}")
        if path.suffix != ".pusingcuk":
            raise ModuleImportError(f"ekstensi modul harus .pusingcuk: {path.name}")
        if depth > max_depth:
            raise ModuleImportError("batas kedalaman impor modul tercapai")
        if path in active:
            chain = " -> ".join(p.name for p in active + [path])
            raise ModuleImportError(f"siklus impor modul: {chain}")
        if path in cache:
            return cache[path]
        if len(cache) >= max_modules:
            raise ModuleImportError("batas jumlah modul tercapai")
        active.append(path)
        try:
            body = _body(read_source(path), path)
            imports: dict[str, dict[str, str]] = {}
            ordered: list[tuple[Path, str]] = []
            included: set[Path] = set()
            retained: list[str] = []
            exports: list[str] = []
            for line in body:
                match = _IMPORT.fullmatch(line)
                if match:
                    if line != line.lstrip():
                        raise ModuleImportError(f"{path.name}: impor harus di tingkat teratas")
                    raw_name, alias = match.groups()
                    if alias in imports:
                        raise ModuleImportError(f"{path.name}: alias impor '{alias}' ganda")
                    relative = Path(raw_name)
                    if relative.is_absolute() or ".." in relative.parts:
                        raise ModuleImportError(f"{path.name}: jalur impor tidak aman")
                    # Compiler-only static expansion follows the interpreter rule:
                    # resolve each import from the file that declares it, not CWD.
                    target = (path.parent / relative).resolve()
                    child_modules, module_exports = load(target, depth + 1)
                    for child_path, child_code in child_modules:
                        if child_path not in included:
                            ordered.append((child_path, child_code))
                            included.add(child_path)
                    imports[alias] = module_exports
                    continue
                if line.lstrip().startswith("pakai "):
                    raise ModuleImportError(f"{path.name}: sintaks impor tidak valid")
                exp = _EXPORT.fullmatch(line)
                if exp:
                    exports.append(exp.group(1))
                    continue
                retained.append(line)

            functions = [m.group(1) for line in retained
                         if (m := _FUNCTION.match(line))]
            if len(functions) != len(set(functions)):
                raise ModuleImportError(f"{path.name}: nama fungsi duplikat")
            if len(exports) != len(set(exports)):
                raise ModuleImportError(f"{path.name}: deklarasi ekspor duplikat")
            missing = sorted(set(exports) - set(functions))
            if missing:
                raise ModuleImportError(
                    f"{path.name}: ekspor bukan fungsi yang didefinisikan: {', '.join(missing)}"
                )
            prefix = "_pcmod_" + hashlib.sha256(
                path.relative_to(root).as_posix().encode("utf-8")
            ).hexdigest()[:10] + "_"
            own_names = {name: prefix + name for name in functions}
            if set(imports) & set(functions):
                raise ModuleImportError(f"{path.name}: alias modul bentrok dengan nama fungsi")
            rewritten = _rewrite("\n".join(retained) + "\n", own_names, imports, path)
            ordered.append((path, rewritten))
            module_exports = {name: own_names[name] for name in exports}
            cache[path] = (ordered, module_exports)
            return cache[path]
        finally:
            active.pop()

    entry_body = _body(read_source(entry), entry)
    imports: dict[str, dict[str, str]] = {}
    ordered: list[tuple[Path, str]] = []
    included: set[Path] = set()
    retained: list[str] = []
    for line in entry_body:
        match = _IMPORT.fullmatch(line)
        if match:
            if line != line.lstrip():
                raise ModuleImportError("impor harus berada di tingkat teratas")
            raw_name, alias = match.groups()
            if alias in imports:
                raise ModuleImportError(f"alias impor '{alias}' ganda")
            relative = Path(raw_name)
            if relative.is_absolute() or ".." in relative.parts:
                raise ModuleImportError("jalur impor tidak aman")
            # The entry file is the caller for top-level compiler imports; nested
            # imports above are resolved from their own declaring module file.
            target = (entry.parent / relative).resolve()
            modules, module_exports = load(target, 1)
            for module_path, module_code in modules:
                if module_path not in included:
                    ordered.append((module_path, module_code))
                    included.add(module_path)
            imports[alias] = module_exports
        elif line.lstrip().startswith("pakai "):
            raise ModuleImportError("sintaks impor tidak valid")
        else:
            retained.append(line)
    main_code = _rewrite("\n".join(retained) + "\n", {}, imports, entry)
    body = "\n".join([code for _path, code in ordered] + [main_code])
    return "jancuk\n" + body + "selesai jancuk\n"
