"""Generate a standalone HTML wrapper for a canonical PusingCuk IR document."""
from compiler.js_backend import generate as generate_javascript


def generate(document: dict) -> str:
    """Compile one canonical IR document into a self-contained HTML page."""
    javascript = generate_javascript(document)
    return (
        '<!doctype html>\n<html lang="id">\n<head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>PusingCuk</title></head>\n<body><pre id="pc-output"></pre>\n'
        '<script>\n'
        'const pcOutput = document.getElementById("pc-output");\n'
        'const console = {log: (...args) => { pcOutput.textContent += args.join(" ") + "\\n"; }, '
        'error: (...args) => { globalThis.console.error(...args); }};\n'
        'const process = {exitCode: 0};\n'
        + javascript
        + '\n</script>\n</body>\n</html>\n'
    )
