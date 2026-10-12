"""Formatter sederhana untuk indentasi sumber Pusingcuk (2 spasi per level)."""
from pathlib import Path


_BLOCK_STARTS = {"coba", "njir", "mumet", "untuk", "fungsi"}
_BRANCH_MARKERS = {"ketangkep": "coba", "akhirnya": "coba", "kampret": "njir"}


def format_source(source):
    """Normalize indentation and align block terminators with their opener."""
    if not source:
        return source

    output = []
    stack = []
    for raw_line in source.splitlines():
        line = raw_line.strip()
        if not line:
            output.append("")
            continue

        first = line.split(None, 1)[0]
        words = line.split()

        if first == "jancuk":
            stack = ["jancuk"]
            output.append("jancuk")
            continue

        if first == "selesai":
            closing = words[1] if len(words) > 1 else ""
            if closing == "jancuk":
                stack = []
                indent = 0
            else:
                if stack and stack[-1] == closing:
                    stack.pop()
                elif stack and stack[-1] != "jancuk":
                    # Keep indentation stable even when the source has a typo.
                    stack.pop()
                indent = len(stack)
            output.append(" " * (2 * indent) + line)
            continue

        if first in _BRANCH_MARKERS:
            opener = _BRANCH_MARKERS[first]
            index = next(
                (i for i in range(len(stack) - 1, -1, -1) if stack[i] == opener),
                None,
            )
            indent = index if index is not None else len(stack)
            output.append(" " * (2 * indent) + line)
            continue

        indent = len(stack)
        output.append(" " * (2 * indent) + line)
        if first in _BLOCK_STARTS:
            stack.append(first)

    return "\n".join(output).rstrip("\n") + "\n"


def format_file(path):
    """Format a .pusingcuk file in place and return its formatted contents."""
    path = Path(path)
    if path.suffix != ".pusingcuk":
        raise ValueError("formatter hanya menerima berkas .pusingcuk")
    source = path.read_text(encoding="utf-8")
    formatted = format_source(source)
    path.write_text(formatted, encoding="utf-8")
    return formatted
