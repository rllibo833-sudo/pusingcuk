"""Public compiler API and module entrypoint."""
from __future__ import annotations

import json
from typing import Any

from compiler.ir import dumps, from_source
from compiler.self_hosted_frontend import from_source as self_hosted_from_source


def compile_source(
    source: str,
    source_name: str = "<memory>",
    target: str = "json",
    frontend: str = "reference",
) -> str:
    """Compile source to a supported target while preserving the historical API."""
    if frontend == "reference":
        document = from_source(source, source_name)
    elif frontend == "selfhosted":
        document = self_hosted_from_source(source, source_name)
    else:
        raise ValueError(f"frontend tidak dikenal: {frontend}")
    if target == "json":
        return dumps(document)
    if target == "js":
        from compiler.js_backend import generate
        return generate(document)
    if target == "python":
        from compiler.python_backend import generate
        return generate(document)
    if target == "c":
        from compiler.c_backend import generate
        return generate(document)
    if target == "cpp":
        from compiler.cpp_backend import generate
        return generate(document)
    if target == "go":
        from compiler.go_backend import generate
        return generate(document)
    if target == "rust":
        from compiler.rust_backend import generate
        return generate(document)
    if target == "html":
        from compiler.html_backend import generate
        return generate(document)
    raise ValueError(f"target tidak dikenal: {target}")


from compiler.self_hosted import main


if __name__ == "__main__":
    raise SystemExit(main())
